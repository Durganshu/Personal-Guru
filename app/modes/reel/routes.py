from flask import render_template, request
from . import reel_bp
from .services.youtube_search import search_youtube_reels
from .services.validator import validate_videos_batch
from .services.logger import SessionLogger
from app.common.storage import load_topic

# Store active session loggers (keyed by session ID) for Reel mode
active_sessions = {}


@reel_bp.route('/<topic_name>')
def mode(topic_name):
    """Render the Reel mode interface."""
    # Ensure Last Opened/Modified is updated
    load_topic(topic_name, update_timestamp=True)
    return render_template('reel/mode.html', topic_name=topic_name)


@reel_bp.route('/api/search', methods=['POST'])
def search_reels():
    """
    Search for YouTube reels/shorts for a given topic.

    ---
    tags:
      - Reels
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - topic
          properties:
            topic:
              type: string
    responses:
      200:
        description: List of video results
        schema:
          type: object
          properties:
            reels:
              type: array
              items:
                type: object
            session_id:
              type: string
            next_page_token:
              type: string
      400:
        description: Topic is required
    """
    try:
        data = request.get_json()
        topic = data.get('topic', '').strip()

        if not topic:
            return {"error": "Topic is required"}, 400

        # Create session logger
        session_logger = SessionLogger(topic)

        # Search for reels (now returns dict with reels and next_page_token)
        search_result = search_youtube_reels(topic)
        videos = search_result['reels']
        next_page_token = search_result.get('next_page_token')

        # Validate videos (check if they're embeddable)
        validated_videos = validate_videos_batch(videos, session_logger)

        # Cap at 12 results for frontend
        validated_videos = validated_videos[:12]

        # Save session log
        session_logger.save()

        # Store session for event tracking with topic and page_token for pagination
        active_sessions[session_logger.session_id] = {
            'logger': session_logger,
            'topic': topic,
            'next_page_token': next_page_token
        }

        return {
            'reels': validated_videos,
            'session_id': session_logger.session_id,
            'next_page_token': next_page_token
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500


@reel_bp.route('/api/video-event', methods=['POST'])
def video_event():
    """
    Track video play/skip events.

    ---
    tags:
      - Reels
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - session_id
            - video_id
            - event_type
          properties:
            session_id:
              type: string
            video_id:
              type: string
            event_type:
              type: string
              enum: ['played', 'skipped', 'auto_skipped']
    responses:
      200:
        description: Event logged successfully
      400:
        description: Missing required fields
      404:
        description: Session not found
    """
    """Track video play/skip events."""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        video_id = data.get('video_id')
        # 'played', 'skipped', 'auto_skipped'
        event_type = data.get('event_type')

        if not all([session_id, video_id, event_type]):
            return {"error": "Missing required fields"}, 400

        # Get session data (now a dict with 'logger' key)
        session_data = active_sessions.get(session_id)
        if session_data:
            session_logger = session_data.get('logger')
            if session_logger:
                session_logger.update_video_interaction(video_id, event_type)
            return {"status": "logged"}
        else:
            return {"error": "Session not found"}, 404

    except Exception as e:
        return {"error": str(e)}, 500


@reel_bp.route('/api/more-reels', methods=['POST'])
def more_reels():
    """
    Fetch more reels for endless scrolling.

    ---
    tags:
      - Reels
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - session_id
          properties:
            session_id:
              type: string
    responses:
      200:
        description: Additional reels for endless scrolling
        schema:
          type: object
          properties:
            reels:
              type: array
              items:
                type: object
            next_page_token:
              type: string
      400:
        description: Session ID is required
      404:
        description: Session not found or no more reels available
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')

        if not session_id:
            return {"error": "Session ID is required"}, 400

        # Get session data
        session_data = active_sessions.get(session_id)
        if not session_data:
            return {"error": "Session not found"}, 404

        topic = session_data.get('topic')
        page_token = session_data.get('next_page_token')

        if not page_token:
            return {"reels": [], "next_page_token": None}

        session_logger = session_data.get('logger')

        # Fetch more reels using pagination
        search_result = search_youtube_reels(topic, max_results=10, page_token=page_token)
        videos = search_result['reels']
        next_page_token = search_result.get('next_page_token')

        # Validate videos
        validated_videos = validate_videos_batch(videos, session_logger) if session_logger else videos

        # Cap at 10 results per batch
        validated_videos = validated_videos[:10]

        # Update session with new page token
        session_data['next_page_token'] = next_page_token

        return {
            'reels': validated_videos,
            'next_page_token': next_page_token
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}, 500
