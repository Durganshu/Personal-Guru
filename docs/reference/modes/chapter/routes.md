---
sidebar_label: routes
title: modes.chapter.routes
---

#### mode

```python
@chapter_bp.route('/<topic_name>')
def mode(topic_name)
```

Render the chapter mode page for a specific topic.

#### generate\_plan

```python
@chapter_bp.route('/generate', methods=['POST'])
def generate_plan()
```

Generate a study plan for a given topic.

---
tags:
  - Plan Generation
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
          description: The topic to learn about
responses:
  200:
    description: Plan generated successfully
    schema:
      type: object
      properties:
        status:
          type: string
        plan:
          type: array
          items:
            type: string
  400:
    description: Topic name required

#### update\_plan

```python
@chapter_bp.route('/<topic_name>/update_plan', methods=['POST'])
def update_plan(topic_name)
```

Update the study plan based on user feedback.

#### learn\_topic

```python
@chapter_bp.route('/learn/<topic_name>/<int:step_index>')
def learn_topic(topic_name, step_index)
```

Render the learning content for a specific step.

#### assess\_step

```python
@chapter_bp.route('/assess/<topic_name>/<int:step_index>', methods=['POST'])
def assess_step(topic_name, step_index)
```

Evaluate user answers for a step&#x27;s assessment.

#### update\_time

```python
@chapter_bp.route('/<topic_name>/update_time/<int:step_index>',
                  methods=['POST'])
def update_time(topic_name, step_index)
```

Update the time spent on a specific step.

#### reset\_quiz

```python
@chapter_bp.route('/reset_quiz/<topic_name>/<int:step_index>',
                  methods=['POST'])
def reset_quiz(topic_name, step_index)
```

Reset the quiz results for a specific step.

#### generate\_audio\_route

```python
@chapter_bp.route('/generate-audio/<int:step_index>', methods=['POST'])
def generate_audio_route(step_index)
```

Generate TTS audio for the teaching material.

#### generate\_podcast\_route

```python
@chapter_bp.route('/generate-podcast/<topic_name>/<int:step_index>',
                  methods=['POST'])
def generate_podcast_route(topic_name, step_index)
```

Generate a podcast episode for the step.

#### complete\_topic

```python
@chapter_bp.route('/complete/<topic_name>')
def complete_topic(topic_name)
```

Render the topic completion page.

#### export\_topic

```python
@chapter_bp.route('/export/<topic_name>')
def export_topic(topic_name)
```

Export the topic content as a Markdown file.

#### export\_topic\_pdf

```python
@chapter_bp.route('/export/<topic_name>/pdf')
def export_topic_pdf(topic_name)
```

Export the topic content as a PDF file.

#### execute\_code

```python
@chapter_bp.route('/execute_code', methods=['POST'])
def execute_code()
```

Execute Python code in the secure sandbox.

---
tags:
  - Code Execution
parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      required:
        - code
      properties:
        code:
          type: string
          description: Python code to execute
responses:
  200:
    description: Execution result
    schema:
      type: object
      properties:
        output:
          type: string
        error:
          type: string
        images:
          type: array
          items:
            type: string
        enhanced_code:
          type: string
  400:
    description: No code provided
