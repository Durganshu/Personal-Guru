from flask import render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app.core.extensions import db
from app.core.models import Book, BookTopic, Topic, ChapterMode
from app.modes.library import library_bp
from app.modes.chapter.agent import ChapterTeachingAgent
from app.common.agents import LibrarianAgent, PlannerAgent
from app.common.vector_db import VectorDB
from markdown_it import MarkdownIt

md = MarkdownIt()

# A global/in-memory VectorDB for searching user's topics
# In a real setup, this would be persisted or re-indexed efficiently
vector_db_cache = {}

def get_user_vector_db(user_id):
    """Initializes and returns the user's vector DB cache."""
    # To keep things light, we rebuild it for the session if it doesn't exist.
    # We use TF-IDF, which is extremely fast for small personal libraries.
    if user_id not in vector_db_cache:
        vdb = VectorDB()
        topics = Topic.query.filter_by(user_id=user_id).all()

        docs = []
        metadata = []
        for t in topics:
            # Combine topic name and its chapter content for rich search context
            content_parts = [t.name]
            # Add chapter content if available (for better semantic matching)
            chapters = ChapterMode.query.filter_by(topic_id=t.id).all()
            for ch in chapters:
                if ch.content:
                    content_parts.append(ch.content)

            full_text = " ".join(content_parts)
            docs.append(full_text)
            metadata.append({"topic_id": t.id, "title": t.name})

        vdb.add_documents(docs, metadata)
        vector_db_cache[user_id] = vdb

    return vector_db_cache[user_id]


@library_bp.route('/')
@login_required
def dashboard():
    """Renders the main Library Dashboard."""
    my_books = Book.query.filter_by(user_id=current_user.userid).order_by(Book.created_at.desc()).all()
    # Discover others' shared books
    shared_books = Book.query.filter_by(is_shared=True).filter(Book.user_id != current_user.userid).order_by(Book.modified_at.desc()).limit(20).all()

    return render_template('library_dashboard.html', my_books=my_books, shared_books=shared_books)

@library_bp.route('/search', methods=['GET'])
@login_required
def search_library():
    """Searches the user's existing topics using VectorDB to curate a book."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({"error": "Query required"}), 400

    vdb = get_user_vector_db(current_user.userid)
    current_topics = Topic.query.filter_by(user_id=current_user.userid).all()

    agent = LibrarianAgent()
    suggestion = agent.search_and_suggest(query, vdb, current_topics)

    if not suggestion:
        return jsonify({"message": "No relevant existing content found. Consider generating a new book."}), 404

    return jsonify(suggestion)

@library_bp.route('/generate', methods=['POST'])
@login_required
def generate_book():
    """Generates a new book structure using Agentic planning."""
    data = request.json
    query = data.get('query')

    if not query:
        return jsonify({"error": "Query required"}), 400

    user_bg = current_user.user_profile.to_context_string() if current_user.user_profile else "A beginner"
    agent = LibrarianAgent()
    book_plan = agent.generate_book(query, user_bg)

    # Actually create the shell book and topics in DB
    try:
        new_book = Book(
            user_id=current_user.userid,
            title=book_plan.get('title', f"Book on {query}"),
            description=book_plan.get('description', ''),
            is_shared=False
        )
        db.session.add(new_book)
        db.session.flush() # Get new_book IDs

        # Create empty Topics for each chapter in the plan
        for idx, topic_title in enumerate(book_plan.get('topics', [])):
            t = Topic(
                name=topic_title,
                user_id=current_user.userid
            )
            db.session.add(t)
            db.session.flush() # Get t.id

            bt = BookTopic(
                book_id=new_book.id,
                topic_id=t.id,
                order_index=idx
            )
            db.session.add(bt)

        db.session.commit()
        # Invalidate vector DB cache
        if current_user.userid in vector_db_cache:
            del vector_db_cache[current_user.userid]

        return jsonify({
            "success": True,
            "book": {"id": new_book.id, "title": new_book.title},
            "redirect": url_for('library.read_book', book_id=new_book.id, page_num=1)
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@library_bp.route('/create-from-suggestion', methods=['POST'])
@login_required
def create_from_suggestion():
    """Creates a book containing the curated existing topics."""
    data = request.json
    title = data.get('title')
    desc = data.get('description')
    topic_ids = data.get('topic_ids', [])

    if not title or not topic_ids:
        return jsonify({"error": "Invalid data"}), 400

    try:
        b = Book(
            user_id=current_user.userid,
            title=title,
            description=desc,
            is_shared=False
        )
        db.session.add(b)
        db.session.flush()

        for idx, tid in enumerate(topic_ids):
            # Verify user owns topic
            t = Topic.query.filter_by(id=tid, user_id=current_user.userid).first()
            if t:
                bt = BookTopic(book_id=b.id, topic_id=t.id, order_index=idx)
                db.session.add(bt)

        db.session.commit()
        return jsonify({"success": True, "book_id": b.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@library_bp.route('/<int:book_id>/init')
@login_required
def init_book(book_id):
    """
    Initializes a book before reading. Checks all topics and chapters.
    If a topic lacks chapters (not yet generated), it uses PlannerAgent to generate a plan.
    If a chapter lacks teaching material, it uses ChapterTeachingAgent to generate it.
    This ensures the book is fully readable when opened.
    """
    book = Book.query.get_or_404(book_id)

    if book.user_id != current_user.userid and not book.is_shared:
        return render_template('error.html', error_message="You don't have permission to view this book."), 403

    planner = PlannerAgent()
    teacher = ChapterTeachingAgent()

    from app.common.utils import get_user_context
    user_background = get_user_context()

    # Pre-generate any missing content for the entire book
    for bt in book.book_topics:
        topic = bt.topic
        # 1. Check if the topic has a plan (chapters)
        chapters = ChapterMode.query.filter_by(topic_id=topic.id).order_by(ChapterMode.step_index).all()
        if not chapters:
            try:
                plan_steps = planner.generate_study_plan(topic.name, user_background)
                from app.common.storage import load_topic, save_topic
                # Generate topic JSON data structure
                topic_data = load_topic(topic.name) or {"name": topic.name}
                topic_data['plan'] = plan_steps
                topic_data['chapter_mode'] = [{'title': step_title, 'step_index': i} for i, step_title in enumerate(plan_steps)]
                save_topic(topic.name, topic_data)

                # Fetch newly created chapters from DB
                chapters = ChapterMode.query.filter_by(topic_id=topic.id).order_by(ChapterMode.step_index).all()
            except Exception as e:
                # Log error and continue to the next topic (graceful degradation)
                print(f"Failed to generate plan for {topic.name}: {e}")
                continue

        # 2. Check each chapter for teaching material
        topic_data = None
        for chapter in chapters:
            if not chapter.content:
                if not topic_data:
                    from app.common.storage import load_topic
                    topic_data = load_topic(topic.name)

                try:
                    plan_steps = topic_data.get('plan', [])
                    step_title = plan_steps[chapter.step_index] if chapter.step_index < len(plan_steps) else "Chapter Content"
                    material = teacher.generate_teaching_material(step_title, plan_steps, user_background, None)

                    # Save to JSON storage and DB
                    topic_data['chapter_mode'][chapter.step_index]['teaching_material'] = material
                    from app.common.storage import save_topic
                    save_topic(topic.name, topic_data)

                    # Ensure DB model is updated in current session
                    chapter.content = material
                except Exception as e:
                    print(f"Failed to generate material for {topic.name} chapter {chapter.step_index}: {e}")

    db.session.commit()
    return redirect(url_for('library.read_book', book_id=book.id, page_num=1))


@library_bp.route('/<int:book_id>/page/<int:page_num>')
@login_required
def read_book(book_id, page_num):
    """
    Paginated Book View Interface.
    Maps page_num to the flattened list of chapters across all topics in the book.
    """
    book = Book.query.get_or_404(book_id)

    # Check permissions
    if book.user_id != current_user.userid and not book.is_shared:
        return render_template('error.html', error_message="You don't have permission to view this book."), 403

    # Get all ordered topics in the book
    book_topics = sorted(book.book_topics, key=lambda x: x.order_index)
    topics = [bt.topic for bt in book_topics]

    # For pagination, we flatten chapters from topics (Page 1 = Topic1/Chapter1... )
    # This requires looking up all chapters for these topics.
    flattened_pages = []

    for topic_idx, t in enumerate(topics):
        chapters = ChapterMode.query.filter_by(topic_id=t.id).order_by(ChapterMode.step_index).all()
        # If no chapters yet, we treat the topic itself as a pending 1-page placeholder
        if not chapters:
            flattened_pages.append({
                "type": "placeholder",
                "topic": t,
                "topic_number": topic_idx + 1,
                "chapter": None,
                "global_page": len(flattened_pages) + 1
            })
        else:
            for ch in chapters:
                flattened_pages.append({
                    "type": "content",
                    "topic": t,
                    "topic_number": topic_idx + 1,
                    "chapter": ch,
                    "global_page": len(flattened_pages) + 1
                })

    total_pages = len(flattened_pages)

    if page_num < 1 or page_num > total_pages:
        if total_pages == 0:
             return render_template('book_view.html', book=book, current_page_data=None, page_num=0, total_pages=0)
        return redirect(url_for('library.read_book', book_id=book.id, page_num=max(1, min(page_num, total_pages))))

    current_page_data = flattened_pages[page_num - 1]

    # Convert markdown to html if this is a content page
    if current_page_data["type"] == "content" and current_page_data["chapter"].content:
        # We need a copy or attribute to store rendered html so we don't save raw html to DB
        current_page_data["chapter_html"] = md.render(current_page_data["chapter"].content)
    else:
        current_page_data["chapter_html"] = ""

    # Handle Notes exposure
    # If viewed by owner, we embed the notes. If viewed by others, we hide notes.
    show_notes = (book.user_id == current_user.userid)

    return render_template(
        'book_view.html',
        book=book,
        current_page_data=current_page_data,
        page_num=page_num,
        total_pages=total_pages,
        show_notes=show_notes
    )

@library_bp.route('/<int:book_id>/toggle-share', methods=['POST'])
@login_required
def toggle_share(book_id):
    """Toggles the is_shared status of a book."""
    book = Book.query.get_or_404(book_id)
    if book.user_id != current_user.userid:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    book.is_shared = data.get('is_shared', False)
    db.session.commit()

    return jsonify({"success": True, "is_shared": book.is_shared})
