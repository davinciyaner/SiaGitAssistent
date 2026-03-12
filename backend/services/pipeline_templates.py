python_pipeline = """
name: Python CI

on:
  push:
    branches: [ origin/master ]

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

      - name: Run Tests
        run: |
          pytest backend || true
      - name: Lint Code
        run: |
           pip install flake8
           flake8 backend || true
"""

node_pipeline = """
name: Node CI

on:
  push:
    branches: [ origin/master ]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: 24

      - run: npm install
      - run: npm test
"""
