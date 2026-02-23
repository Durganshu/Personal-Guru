"""
Robust book content generation with persistent progress tracking.
"""
import datetime
import logging
from threading import Thread
from flask import current_app
from app.core.extensions import db
from app.core.models import Book, BookGenerationProgress, ChapterMode
from app.modes.chapter.agent import ChapterTeachingAgent
from app.common.agents import PlannerAgent

logger = logging.getLogger(__name__)


def start_book_generation(book_id, user_id, user_background):
    """
    Starts background generation for a book.
    Creates or updates progress tracking record.
    """
    # Create or get progress record
    progress = BookGenerationProgress.query.filter_by(book_id=book_id).first()

    book = Book.query.get(book_id)
    if not book:
        logger.error(f"Book {book_id} not found")
        return False

    total_topics = len(book.book_topics)

    if not progress:
        # Create new progress record
        progress = BookGenerationProgress(
            book_id=book_id,
            user_id=user_id,
            status='pending',
            total_topics=total_topics,
            current_topic_index=0,
            total_chapters=0,  # Will be calculated during generation
            completed_chapters=0,
            current_message='Initializing generation...',
            started_at=datetime.datetime.utcnow()
        )
        db.session.add(progress)
        db.session.commit()
    else:
        # Update existing progress record
        if progress.status == 'generating':
            logger.info(f"Book {book_id} is already generating")
            return True

        # Reset progress for retry
        progress.status = 'pending'
        progress.total_topics = total_topics
        progress.current_topic_index = 0
        progress.error_message = None
        progress.current_message = 'Restarting generation...'
        progress.started_at = datetime.datetime.utcnow()
        progress.completed_at = None
        db.session.commit()

    # Start background thread
    app_context = current_app._get_current_object().app_context()
    thread = Thread(
        target=generate_book_content_background,
        args=(app_context, book_id, user_id, user_background)
    )
    thread.daemon = True
    thread.start()

    return True


def generate_book_content_background(app_context, book_id, user_id, user_background):
    """
    Background task to generate all content for a book with persistent progress tracking.
    """
    with app_context:
        progress = None
        try:
            # Get progress record
            progress = BookGenerationProgress.query.filter_by(book_id=book_id).first()
            if not progress:
                logger.error(f"Progress record not found for book {book_id}")
                return

            # Update status to generating
            progress.status = 'generating'
            progress.started_at = datetime.datetime.utcnow()
            db.session.commit()

            # Get book and topics
            book = Book.query.get(book_id)
            if not book:
                raise Exception(f"Book {book_id} not found")

            planner = PlannerAgent()
            teacher = ChapterTeachingAgent()

            total_topics = len(book.book_topics)
            progress.total_topics = total_topics

            # First pass: count total chapters needed
            total_chapters_needed = 0
            for bt in book.book_topics:
                topic = bt.topic
                chapters = ChapterMode.query.filter_by(topic_id=topic.id).all()
                if not chapters:
                    # Estimate 5 chapters per topic (will be updated when plan is generated)
                    total_chapters_needed += 5
                else:
                    total_chapters_needed += len(chapters)

            progress.total_chapters = total_chapters_needed
            db.session.commit()

            # Generate content for each topic
            for idx, bt in enumerate(sorted(book.book_topics, key=lambda x: x.order_index)):
                topic = bt.topic
                progress.current_topic_index = idx
                progress.current_message = f'Processing topic {idx + 1}/{total_topics}: {topic.name}'
                db.session.commit()

                # Check if topic has chapters
                chapters = ChapterMode.query.filter_by(topic_id=topic.id).order_by(ChapterMode.step_index).all()

                if not chapters:
                    # Generate study plan
                    progress.current_message = f'Generating plan for: {topic.name}'
                    db.session.commit()

                    try:
                        plan_steps = planner.generate_study_plan(topic.name, user_background)

                        # Save plan directly to database (bypass storage.py which needs current_user)
                        topic.study_plan = plan_steps

                        # Create chapter records
                        for i, step_title in enumerate(plan_steps):
                            chapter = ChapterMode(
                                user_id=user_id,
                                topic_id=topic.id,
                                step_index=i,
                                title=step_title
                            )
                            db.session.add(chapter)

                        db.session.commit()

                        # Update total chapters count
                        actual_chapters = len(plan_steps)
                        progress.total_chapters = progress.total_chapters - 5 + actual_chapters
                        db.session.commit()

                        # Reload chapters
                        chapters = ChapterMode.query.filter_by(topic_id=topic.id).order_by(ChapterMode.step_index).all()
                    except Exception as e:
                        logger.error(f"Failed to generate plan for {topic.name}: {e}")
                        progress.current_message = f'Error generating plan for {topic.name}: {str(e)}'
                        db.session.commit()
                        continue

                # Generate content for each chapter
                for ch_idx, chapter in enumerate(chapters):
                    if chapter.content:
                        # Already has content, skip
                        progress.completed_chapters += 1
                        db.session.commit()
                        continue

                    progress.current_message = f'Writing {topic.name}: Chapter {ch_idx + 1}/{len(chapters)}'
                    db.session.commit()

                    try:
                        # Get plan steps from topic
                        plan_steps = topic.study_plan if topic.study_plan else []
                        step_title = plan_steps[chapter.step_index] if chapter.step_index < len(plan_steps) else chapter.title or "Chapter Content"

                        # Generate teaching material
                        material = teacher.generate_teaching_material(
                            step_title,
                            plan_steps,
                            user_background,
                            None
                        )

                        # Save to database directly
                        chapter.content = material
                        progress.completed_chapters += 1
                        db.session.commit()

                    except Exception as e:
                        logger.error(f"Failed to generate content for {topic.name} chapter {chapter.step_index}: {e}")
                        progress.current_message = f'Error in {topic.name} chapter {ch_idx + 1}: {str(e)}'
                        db.session.commit()

            # Mark as completed
            progress.status = 'completed'
            progress.current_message = 'Generation complete!'
            progress.completed_at = datetime.datetime.utcnow()
            db.session.commit()

            logger.info(f"Book {book_id} generation completed successfully")

        except Exception as e:
            logger.error(f"Book generation failed for {book_id}: {e}", exc_info=True)
            if progress:
                progress.status = 'error'
                progress.error_message = str(e)
                progress.completed_at = datetime.datetime.utcnow()
                db.session.commit()


def get_generation_progress(book_id):
    """
    Get the current generation progress for a book.
    Returns a dictionary with progress information.
    """
    progress = BookGenerationProgress.query.filter_by(book_id=book_id).first()

    # Check if book actually needs generation
    book = Book.query.get(book_id)
    if not book:
        return {'status': 'error', 'message': 'Book not found'}

    needs_generation = False
    for bt in book.book_topics:
        chapters = ChapterMode.query.filter_by(topic_id=bt.topic.id).all()
        if not chapters:
            needs_generation = True
            break
        for ch in chapters:
            if not ch.content:
                needs_generation = True
                break
        if needs_generation:
            break

    # If no progress record exists
    if not progress:
        if needs_generation:
            return {'status': 'pending', 'message': 'Ready to generate', 'book_id': book_id}
        else:
            return {'status': 'completed', 'message': 'Already generated', 'book_id': book_id}

    # If progress exists but marked completed, but actually needs generation
    # (e.g., user added new topics to the book)
    if progress.status == 'completed' and needs_generation:
        # Reset progress to pending
        progress.status = 'pending'
        progress.current_message = 'Additional content needed'
        db.session.commit()

    # If progress exists but marked error, and still needs generation
    if progress.status == 'error' and needs_generation:
        # Allow retry by resetting to pending
        progress.status = 'pending'
        progress.error_message = None
        progress.current_message = 'Ready to retry generation'
        db.session.commit()

    return progress.to_dict()


def get_all_active_generations(user_id):
    """
    Get all active book generations for a user.
    Returns a list of progress dictionaries.
    """
    active_progress = BookGenerationProgress.query.filter_by(
        user_id=user_id
    ).filter(
        BookGenerationProgress.status.in_(['pending', 'generating'])
    ).all()

    return [p.to_dict() for p in active_progress]
