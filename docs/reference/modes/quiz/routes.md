---
sidebar_label: routes
title: modes.quiz.routes
---

#### generate\_quiz

```python
@quiz_bp.route('/generate/<topic_name>/<count>', methods=['GET', 'POST'])
def generate_quiz(topic_name, count)
```

Generate a quiz with the specified number of questions and save it.

#### mode

```python
@quiz_bp.route('/<topic_name>')
def mode(topic_name)
```

Load quiz from saved data or generate new one.

#### submit\_quiz

```python
@quiz_bp.route('/<topic_name>/submit', methods=['POST'])
def submit_quiz(topic_name)
```

Evaluate and save quiz submissions.

#### update\_time

```python
@quiz_bp.route('/<topic_name>/update_time', methods=['POST'])
def update_time(topic_name)
```

Update total time spent on the quiz.

#### export\_quiz\_pdf

```python
@quiz_bp.route('/<topic_name>/export/pdf')
def export_quiz_pdf(topic_name)
```

Export the most recent quiz results as a PDF.

#### reset\_quiz

```python
@quiz_bp.route('/<topic_name>/reset', methods=['POST'])
def reset_quiz(topic_name)
```

Reset the quiz to allow regeneration.
