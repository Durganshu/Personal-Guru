## 1. Overview
The Library is a central repository for all learned topics, organized into "Books". It provides users with a structured way to manage, search, and explore their knowledge base, including chapter content and personal notes.

## 2. Goals
- Provide a structured "Book" view for learned topics.
- Enable AI-powered book discovery and generation (The Librarian).
- Support sharing and exploring books from other users.
- Facilitate seamless reading and note-taking through a paginated UI.

## 3. User Stories
- **As a learner**, I want to search for books by topic, course name, or content so that I can find relevant study materials.
- **As a learner**, I want the "Librarian" to suggest books based on my query so that I don't have to manually organize topics.
- **As a learner**, I want to toggle between my books, others' shared books, and generating new books.
- **As a learner**, I want to read books in a paginated format where each page is a chapter/topic.
- **As a learner**, I want to see my notes alongside the chapters in the same paginated format.

## 4. Functional Requirements

### 4.1 Data Model Extensions (app/core/models.py)
- **Book Model**:
    - `id`: Primary Key.
    - `user_id`: Foreign Key to `logins.userid`.
    - `title`: String (255), the name of the book.
    - `description`: Text, a brief summary of the book.
    - `is_shared`: Boolean, default False.
    - `created_at`, `modified_at`: Timestamps.
- **BookTopic Model** (Many-to-Many relationship):
    - `book_id`: Foreign Key to `books.id`.
    - `topic_id`: Foreign Key to `topics.id`.
    - `order_index`: Integer, to maintain the sequence of topics within the book.

### 4.2 Librarian Agent (app/common/agents.py)
- **Search & Suggestion**:
    - Accepts a query (topic/course name/content).
    - Clusters existing `Topic` and `ChapterMode` content using a graph vector database.
    - Generates book suggestions by identifying related topics.
- **Book Generation**:
    - If "Generate book" is selected, the agent will trigger the creation of new `Topic` entities (using existing `PlannerAgent` and `TopicTeachingAgent`) if the query doesn't match enough existing content.

### 4.3 Library UI/UX
- **Search Interface**:
    - Input field for query.
    - Toggle button: `[Search My Books | Search Others' Books | Generate Book]`.
- **Book Exploration**:
    - Conventional pagination pattern.
    - Each "Page" = One `ChapterMode` step from a `Topic`.
    - Sequential topics: When one topic's chapters end, the next topic in the book begins on the next page.
    - **Notebook View**: A mirrored pagination for `Topic.notes`, allowing users to see their notes for each chapter.

### 4.4 Sharing Logic
- Users can toggle `is_shared` for their books.
- "Search Others' Books" displays shared books from other users.
- **Security**: When reading a shared book, the original author's notes are **NOT** shared. The reader can create their own notes for the shared book's topics.

## 5. Technical Requirements

### 5.1 Graph Vector Database (app/common/vector_db.py)
- Upgrade the stub `VectorDB` to support:
    - Embedding generation for `Topic` names, `ChapterMode` content, and `Topic` notes.
    - Storing relationships (edges) between topics to facilitate clustering.
    - Similarity search for book discovery.

### 5.2 API Routes (app/core/routes.py or new app/modes/library/routes.py)
- `GET /library`: Render the library dashboard.
- `GET /api/library/search`: Search books based on toggle state.
- `POST /api/library/create-book`: Create a book from selected/suggested topics.
- `GET /book/<int:book_id>/page/<int:page_num>`: Fetch specific chapter content.

## 6. Acceptance Criteria
- [ ] Users can create a "Book" by selecting multiple topics.
- [ ] The Librarian correctly suggests existing topics based on a keyword search.
- [ ] The paginated UI correctly loads chapters across multiple topics in a book.
- [ ] Shared books are visible to other users but do not expose personal notes.
- [ ] The "Generate Book" mode successfully creates new topics when needed.
