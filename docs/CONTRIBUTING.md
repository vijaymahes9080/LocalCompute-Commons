# Contributing to LocalCompute Commons

We welcome contributions from researchers, students, and open-source engineers!

## 1. Development Workflow
1. Fork and clone the repository.
2. Create a feature branch: `git checkout -b feature/my-feature`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Ensure all unit and integration tests pass:
   ```bash
   pytest tests/ -v
   python tests/evaluation/run_evaluations.py
   ```
5. Ensure frontend builds cleanly:
   ```bash
   cd apps/web && npm run build
   ```
6. Submit a Pull Request.

## 2. Code Standards
- Strict type hinting in Python with Pydantic v2 schemas.
- Strict TypeScript in React frontend.
- Preserve zero-trust security invariants: all API inputs validated, no arbitrary shell execution.
