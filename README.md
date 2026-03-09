# SIA — Simple Git Assistant

A lightweight developer tool that simplifies common Git workflows by combining multiple Git commands into simple instructions.

Instead of remembering and typing several Git commands, you can execute a single command and **SIA handles the rest automatically**.

---

# Why SIA?

Working with Git can be confusing, especially for beginners.
Many workflows require multiple commands executed in the correct order.

SIA simplifies this process by allowing developers to run **simple instructions that automate common Git operations**.

Example:

Instead of typing:


1. git init
2. git add .
3. git commit -m "Initial commit"
4. git branch main
5. git push -u origin main


You can simply run:


**init myproject**


SIA automatically executes the required steps.

---

# Features

- Repository initialization
- Git command automation
- Branch creation with optional GitHub push
- Simplified commit workflow
- Pull request creation
- GitHub authentication
- Simple command interface

---

# Example Workflow

### Initialize a project


init myproject


### Create a branch and push it to GitHub


branch myproject feature-login --push


### Commit changes


commit myproject


### Push changes


push myproject


### Create a pull request


pr myproject in main


---

# Commands

| Command | Description |
|------|-------------|
| `init <project>` | Initialize a Git repository and push the initial commit |
| `branch <project> <branch>` | Create a new branch |
| `branch <project> <branch> --push` | Create and push branch to GitHub |
| `checkout <project> <branch>` | Switch to another branch |
| `commit <project>` | Commit current changes |
| `push <project>` | Push commits to GitHub |
| `merge <project> in <branch>` | Merge current branch into target branch |
| `pr <project> in <branch>` | Create a pull request |

---

# Installation

## Clone the repository


git clone https://github.com/YOURUSERNAME/sia.git


---

# Backend Setup

Navigate to the backend directory:


cd backend


Install dependencies:


pip install -r requirements.txt


Start the API server:


uvicorn FastAPI:app --reload


---

# Frontend Setup

Navigate to the frontend directory:


cd frontend


Install dependencies:


npm install


Start the development server:


npm start


---

# Tech Stack

## Backend

- Python
- FastAPI

## Frontend

- React

## Version Control

- Git
- GitHub API

---

# Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

# License

This project is licensed under the **MIT License**.

---

# Future Improvements

Planned improvements include:

- Natural language Git commands
- CLI support
- Extended Git workflow automation
- Improved error handling

---

# Author

Created by **Finn Paustian**

---

# ⭐ Support

If you find this project useful, consider giving it a **star on GitHub**.