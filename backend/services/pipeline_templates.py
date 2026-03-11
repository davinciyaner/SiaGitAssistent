python_pipeline = """
name: Python CI

on:
  push:
    branches: [ origin/master ]

jobs:
  build:

    runs-on: ubuntu-latest

    steps:

      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run Tests
        run: |
          pytest
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
          node-version: 18

      - run: npm install
      - run: npm test
"""

