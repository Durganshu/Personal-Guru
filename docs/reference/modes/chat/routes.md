---
sidebar_label: routes
title: modes.chat.routes
---

#### mode

```python
@chat_bp.route('/<topic_name>')
def mode(topic_name)
```

Render the main chat interface for a topic.

#### update\_plan

```python
@chat_bp.route('/<topic_name>/update_plan', methods=['POST'])
def update_plan(topic_name)
```

Handle study plan modification requests from user feedback.

#### send\_message

```python
@chat_bp.route('/<topic_name>/send', methods=['POST'])
def send_message(topic_name)
```

Process and respond to a user chat message.

#### update\_time

```python
@chat_bp.route('/<topic_name>/update_time', methods=['POST'])
def update_time(topic_name)
```

Update time spent on chat session.

#### chat

```python
@chat_bp.route('/<topic_name>/<int:step_index>', methods=['GET', 'POST'])
def chat(topic_name, step_index)
```

Handle popup chat messages within chapter steps.

---
tags:
  - Chat
parameters:
  - name: topic_name
    in: path
    type: string
    required: true
  - name: step_index
    in: path
    type: integer
    required: true
    description: Step index or 9999 for general chat
  - in: body
    name: body
    required: false
    schema:
      type: object
      required:
        - question
      properties:
        question:
          type: string
        time_spent:
          type: integer
responses:
  200:
    description: AI response or Chat History
    schema:
      type: object
      properties:
        answer:
          type: string
        history:
          type: array
          items:
            type: object
            properties:
              role:
                type: string
              content:
                type: string
  400:
    description: Invalid request
  500:
    description: Processing error
