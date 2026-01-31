---
sidebar_label: routes
title: modes.flashcard.routes
---

#### mode

```python
@flashcard_bp.route('/<topic_name>')
def mode(topic_name)
```

Display flashcard mode with saved flashcards or generation UI.

#### generate\_flashcards\_route

```python
@flashcard_bp.route('/generate', methods=['POST'])
def generate_flashcards_route()
```

Generate flashcards for a topic.

---
tags:
  - Flashcards
parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      properties:
        topic:
          type: string
        count:
          type: string
          description: Number of cards or &#x27;auto&#x27;
          default: &#x27;auto&#x27;
responses:
  200:
    description: Generated flashcards
    schema:
      type: object
      properties:
        flashcards:
          type: array
          items:
            type: object
  400:
    description: No topic provided

#### update\_time

```python
@flashcard_bp.route('/<topic_name>/update_time', methods=['POST'])
def update_time(topic_name)
```

Update time spent on flashcards.

#### update\_progress

```python
@flashcard_bp.route('/<topic_name>/update_progress', methods=['POST'])
def update_progress(topic_name)
```

Update progress/time-spent for specific flashcards.

---
tags:
  - Flashcards
parameters:
  - name: topic_name
    in: path
    type: string
    required: true
  - in: body
    name: body
    required: true
    schema:
      type: object
      properties:
        flashcards:
          type: array
          items:
            type: object
responses:
  200:
    description: Progress updated successfully
  404:
    description: Topic not found

#### export\_pdf

```python
@flashcard_bp.route('/<topic_name>/export/pdf')
def export_pdf(topic_name)
```

Export flashcards as a PDF.

#### reset\_flashcards

```python
@flashcard_bp.route('/<topic_name>/reset', methods=['POST'])
def reset_flashcards(topic_name)
```

Reset the flashcards to allow regeneration.
