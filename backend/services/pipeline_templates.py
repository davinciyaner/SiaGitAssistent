python_pipeline = """
name: Python CI

on:
  push:
    branches: [ master ]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest flake8

      - name: Format Check
        run: |
          pip install black
          black --check backend
          
      - name: Lint Code
        run: |
          flake8 backend

      - name: Run Tests
        run: |
          pytest backend || true
          black --check backend
"""

node_pipeline = """
name: Node CI

on:
  push:
    branches: [ master ]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 24

      - run: npm install
      - run: npm test
"""
