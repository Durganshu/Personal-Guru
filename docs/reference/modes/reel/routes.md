---
sidebar_label: routes
title: modes.reel.routes
---

#### mode

```python
@reel_bp.route('/<topic_name>')
def mode(topic_name)
```

Render the Reel mode interface.

#### search\_reels

```python
@reel_bp.route('/api/search', methods=['POST'])
def search_reels()
```

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
  400:
    description: Topic is required

#### video\_event

```python
@reel_bp.route('/api/video-event', methods=['POST'])
def video_event()
```

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
          enum: [&#x27;played&#x27;, &#x27;skipped&#x27;, &#x27;auto_skipped&#x27;]
responses:
  200:
    description: Event logged successfully
  400:
    description: Missing required fields
  404:
    description: Session not found
