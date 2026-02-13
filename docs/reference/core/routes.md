---
sidebar_label: routes
title: core.routes
---

#### index

```python
@main_bp.route('/', methods=['GET', 'POST'])
def index()
```

Render home page with topics list or redirect to selected learning mode.

#### favicon

```python
@main_bp.route('/favicon.ico')
def favicon()
```

Serve the favicon.ico file.

#### inject\_notifications

```python
@main_bp.app_context_processor
def inject_notifications()
```

Make notifications available to all templates.

#### inject\_jwe

```python
@main_bp.app_context_processor
def inject_jwe()
```

Inject JWE token into all templates.
This allows the frontend to read it from a meta tag and send it in headers.

#### login

```python
@main_bp.route('/login', methods=['GET', 'POST'])
def login()
```

Handle user login with username and password authentication.

#### signup

```python
@main_bp.route('/signup', methods=['GET', 'POST'])
def signup()
```

Handle new user registration and profile creation.

#### logout

```python
@main_bp.route('/logout')
def logout()
```

Log out the current user and redirect to home page.

#### user\_profile

```python
@main_bp.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile()
```

Display and update user profile information.

#### delete\_account

```python
@main_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account()
```

Permanently delete the current user&#x27;s account and all associated data.

#### delete\_topic\_route

```python
@main_bp.route('/delete/<topic_name>')
def delete_topic_route(topic_name)
```

Delete the specified topic and redirect to home page.

#### suggest\_topics

```python
@main_bp.route('/api/suggest-topics', methods=['GET', 'POST'])
@login_required
def suggest_topics()
```

Generate AI-powered topic suggestions based on user profile.

---
tags:
  - Suggestions
responses:
  200:
    description: List of suggested topics
    schema:
      type: object
      properties:
        suggestions:
          type: array
          items:
            type: string
  500:
    description: Internal Server Error

#### settings

```python
@main_bp.route('/settings', methods=['GET', 'POST'])
def settings()
```

Display and update application settings stored in .env file.

POST:
    - Updates .env configuration.
    - Triggers application restart by touching run.py.
    - Returns a client-side polling page to redirect user after restart.

#### transcribe

```python
@main_bp.route('/api/transcribe', methods=['POST'])
@login_required
def transcribe()
```

Transcribe uploaded audio file to text using STT service.

---
tags:
  - Audio
parameters:
  - name: audio
    in: formData
    type: file
    required: true
    description: Audio file to transcribe
responses:
  200:
    description: Transcription result
    schema:
      type: object
      properties:
        transcript:
          type: string
  400:
    description: No audio file provided

#### submit\_feedback

```python
@main_bp.route('/api/feedback', methods=['POST'])
def submit_feedback()
```

Handle user feedback form submissions.

Accepts JSON with feedback_type, rating (1-5), and comment.
Saves to the Feedback table and logs telemetry event.

---
tags:
  - Feedback
parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      required:
        - feedback_type
        - comment
      properties:
        feedback_type:
          type: string
          enum: [&#x27;form&#x27;, &#x27;in_place&#x27;]
        rating:
          type: integer
          minimum: 1
          maximum: 5
        comment:
          type: string
responses:
  200:
    description: Feedback submitted successfully
  400:
    description: Invalid input

#### enforce\_jwe\_security

```python
@main_bp.before_app_request
def enforce_jwe_security()
```

Enforce Dual Token Security (CSRF + JWE) for state-changing requests.

- CSRF is handled by Flask-WTF globally.
- JWE is handled here.

If the request is state-changing (POST, PUT, DELETE, PATCH) and the user is authenticated,
we REQUIRE a valid JWE token (from the X-JWE-Token header, form field &#x27;jwe_token&#x27;, or JSON body field &#x27;jwe_token&#x27;) that matches the current user.
