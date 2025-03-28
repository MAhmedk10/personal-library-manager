import streamlit as st
import sqlite3
import pandas as pd

# --- Database Initialization ---
DATABASE_NAME = "personal_library.db"

def create_table():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            genre TEXT,
            publication_year INTEGER,
            isbn TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

create_table()

# --- Database Interaction Functions ---
def add_book(title, author, genre, publication_year, isbn):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO books (title, author, genre, publication_year, isbn)
            VALUES (?, ?, ?, ?, ?)
        """, (title, author, genre, publication_year, isbn))
        conn.commit()
        st.success(f"Book '{title}' by {author} added successfully!")
    except sqlite3.IntegrityError:
        st.error(f"A book with ISBN '{isbn}' already exists.")
    conn.close()

def view_books():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM books")
    books = cursor.fetchall()
    conn.close()
    return books

def search_books(query, search_by):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    if search_by == "title":
        cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + query + '%',))
    elif search_by == "author":
        cursor.execute("SELECT * FROM books WHERE author LIKE ?", ('%' + query + '%',))
    elif search_by == "genre":
        cursor.execute("SELECT * FROM books WHERE genre LIKE ?", ('%' + query + '%',))
    elif search_by == "isbn":
        cursor.execute("SELECT * FROM books WHERE isbn LIKE ?", ('%' + query + '%',))
    books = cursor.fetchall()
    conn.close()
    return books

def delete_book(book_id):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Check if the book exists
    cursor.execute("SELECT * FROM books WHERE id=?", (book_id,))
    book = cursor.fetchone()
    
    if book:
        cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
        conn.commit()
        st.warning(f"Book with ID {book_id} deleted.")
    else:
        st.warning(f"No book found with ID {book_id}. Please check the ID and try again.")
    
    conn.close()

#     st.markdown(
#     """
#     <style>
#     body {
#         background-color: #f0f8ff; /* Light blue background */
#     }
#     .st-sidebar {
#         background-color: #e0f2f7; /* Lighter blue sidebar */
#     }
#     h1, h2, h3 {
#         color: #336699; /* Darker blue headings */
#     }
#     .stButton>button {
#         background-color: #4CAF50; /* Green button */
#         color: white;
#         border: none;
#         padding: 10px 20px;
#         text-align: center;
#         text-decoration: none;
#         display: inline-block;
#         font-size: 16px;
#         margin: 4px 2px;
#         cursor: pointer;
#         border-radius: 5px;
#     }
#     .stDataFrame {
#         border: 1px solid #ccc;
#         border-radius: 5px;
#         padding: 10px;
#         background-color: white;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# --- Streamlit Web App ---
st.title("📚 Personal Library Manager")
st.subheader("Manage your book collection easily!")

menu = st.sidebar.radio("Navigation", ["Add Book", "View Library", "Search Books"])

if menu == "Add Book":
    st.subheader("Add a New Book")
    title = st.text_input("Title:")
    author = st.text_input("Author:")
    genre = st.text_input("Genre (optional):")
    publication_year = st.number_input("Publication Year (optional):", min_value=0, max_value=2100, step=1, format="%d")
    isbn = st.text_input("ISBN (Unique):")

    if st.button("Add Book"):
        if title and author and isbn:
            add_book(title, author, genre, publication_year, isbn)
        else:
            st.error("Title, Author, and ISBN are required fields.")

elif menu == "View Library":
    st.subheader("Your Library")
    books = view_books()
    if books:
        df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Genre", "Publication Year", "ISBN"])
        st.dataframe(df)

        st.subheader("Delete a Book")
        book_id_to_delete = st.number_input("Enter the ID of the book to delete:", min_value=1, step=1)
        if st.button("Delete Book"):
            delete_book(book_id_to_delete)
            # Refresh the book list after deletion
            books = view_books()
            if books:
                df = pd.DataFrame(books, columns=["ID", "Title", "Author", "Genre", "Publication Year", "ISBN"])
                st.dataframe(df)
            else:
                st.info("Your library is now empty.")
    else:
        st.info("Your library is currently empty. Add some books!")

elif menu == "Search Books":
    st.subheader("Search Your Library")
    search_query = st.text_input("Enter your search term:")
    search_by = st.selectbox("Search by:", ["title", "author", "genre", "isbn"])

    if st.button("Search"):
        if search_query:
            results = search_books(search_query, search_by)
            if results:
                st.subheader("Search Results:")
                df_results = pd.DataFrame(results, columns=["ID", "Title", "Author", "Genre", "Publication Year", "ISBN"])
                st.dataframe(df_results)
            else:
                st.info("No books found matching your search criteria.")
        else:
            st.warning("Please enter a search term.")
