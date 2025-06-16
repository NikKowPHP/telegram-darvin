
## ⚙️ Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker:** The system's memory (Qdrant vector database) runs in a Docker container. [Install Docker](https://docs.docker.com/get-docker/).
*   **Python 3.9+:** [Install Python](https://www.python.org/downloads/).
*   **Roo (`roo-cline`):** The AI agent runner. This is best installed as a VS Code extension. [Get the Roo extension for VS Code](https://marketplace.visualstudio.com/items?itemName=rooveterinaryinc.roo-cline).

---

## 🚀 Easy 1-Click Setup

This project includes an automated setup script to prevent environment issues. It will:
1.  Remove any old, broken virtual environments.
2.  Create a fresh, clean virtual environment.
3.  Install all required Python dependencies into it.

**1. Run the Setup Script**

Open your terminal in the project's root directory and run the following two commands:

```bash
# Make the script executable (you only need to do this once)
chmod +x setup_enviroment.sh && ./setup_enviroment.sh && 
python3 -m venv .venv && source .venv/bin/activate



```

The script will guide you through the process. Once it finishes, your Python environment is ready.

**2. Configure VS Code (Critical for Roo Extension)**

After the script completes successfully, you must tell VS Code to use the new virtual environment. This ensures the Roo extension runs with the correct tools.

*   In VS Code, open the **Command Palette** (`Ctrl+Shift+P` on Windows/Linux, `Cmd+Shift+P` on macOS).
*   Type and select **`Python: Select Interpreter`**.
*   A list of Python interpreters will appear. Choose the one that includes **`./.venv/bin/python`** in its path. It will often be marked as "Recommended".

![VSCode Select Interpreter](https://code.visualstudio.com/assets/docs/python/environments/interpreter-selection.png)

**3. Start the Vector Database**

Before running the agents, make sure the AI's memory (Qdrant) is running via Docker. This command will download the image if you don't have it and run it in the background.
```bash

docker run -d -p 6333:6333 -p 6334:6334 \
    -v qdrant_storage:/qdrant/storage \
    --name roo-factory-db \
    qdrant/qdrant
    
```

**4. Link Agent Rules & Index the Code**
The final step is to link the agent definitions to Roo and initialize the AI's memory with the current state of the code.

```bash
# Link the custom agent definitions from .roo/ to your Roo configuration
./copy_script.sh

# Index the entire project so the agents know what code exists
cct index
```

**That's it!** You are now ready to use the Roo VS Code extension to run the AI agents.

---

## 📖 How to Use the Factory

The system is controlled by giving it a task and then kicking off the `Orchestrator` agent. The Orchestrator analyzes the project state and delegates work to the correct specialist agent.

**Your only action to start or resume work is always to run the `orchestrator` agent from the Roo VS Code extension UI.**

### Scenario 1: Starting a New Project from an Idea

You have an idea for an application but no code. Your task is to describe that idea.

**1. The User's Task: Create `app_description.md`**

In the root of the project, create a new file named `app_description.md`. Be as descriptive as possible.

**Example `app_description.md`:**
```markdown
# Application Idea: Markdown to HTML Blog Post Converter

## Core Functionality
The user should be able to provide a markdown file as input, and the tool should output a styled HTML file.

## Features
- It must support standard markdown syntax (headings, bold, italics, links, images, code blocks).
- The generated HTML should have a clean, readable, default CSS styling.
- It should be a command-line tool with a `--help` flag.
- The user should be able to specify an input file and an optional output file path.
- If no output path is given, it should print the HTML to standard output.
```

**2. How the AI Factory Responds**

Run the `orchestrator` agent.
*   The **Architect** will be activated to create a high-level plan and break down the first phase of work into a `dev_todo_phase_1.md` file.
*   The **Orchestrator** will then hand off to the **Developer**, who begins the Test-Driven Development (TDD) cycle for the first task.
*   The cycle of development, review (`Tech Lead`, `QA Engineer`), and merging will continue until the plan is complete.

### Scenario 2: Adding a New Feature to an Existing Project

Your project is already up and running, and you want to add a new capability.

**1. The User's Task: Create a "Work Item" Ticket**

In the `work_items/` directory (create it if it doesn't exist), create a new `.md` file describing the feature. Use a clear naming convention like `item-XXX-short-description.md`.

**Example `work_items/item-002-add-pdf-export.md`:**
```markdown
---
status: "open"
priority: "high"
---

# Feature Request: Export blog post to PDF

## Description
In addition to HTML, users should be able to export the final blog post as a PDF file.

## Acceptance Criteria
- A new command-line flag, `--pdf <output_path>`, should be added.
- When this flag is used, the tool should convert the markdown to HTML internally, and then render that HTML into a PDF file at the specified output path.
```

**2. How the AI Factory Responds**

Run the `orchestrator` agent.
*   The **Orchestrator** prioritizes open work items. It will see the new ticket and activate the **Architect** for "surgical planning."
*   The **Architect** will use `cct query` to understand existing code and create a specific `dev_todo_item-002.md` plan to implement *only this feature*.
*   The standard development and review cycle will then execute this plan.

### Scenario 3: Fixing a Bug in an Existing Project

You've found a bug and need the AI team to fix it.

**1. The User's Task: Create a "Bug Report" Ticket**

In the `work_items/` directory, create a ticket describing the bug.

**Example `work_items/bug-003-image-links-broken.md`:**
```markdown
---
status: "open"
priority: "critical"
---

# Bug Report: Image links are broken in HTML output

## Steps to Reproduce
1. Create a markdown file with an image link: `![An image](https://example.com/image.png)`
2. Run the tool to convert it to HTML.
3. Open the HTML file in a browser.

## Observed Behavior
The `<img>` tag in the HTML is malformed.

## Expected Behavior
The generated HTML should contain a valid image tag: `<img src="https://example.com/image.png" alt="An image">`.
```

**2. How the AI Factory Responds**

Run the `orchestrator` agent.
*   The flow is identical to adding a feature. The **Orchestrator** assigns the bug report to the **Architect**.
*   The **Developer**'s TDD approach is perfect for bug fixing: it will first write a new test that *fails* because of the bug, and then write the code to make that test pass, ensuring the fix is correct and permanent.

---

## 📺 Monitoring the System

*   **Roo Extension Output:** The VS Code extension's output window provides a live stream of which agent is active and its thought process.
*   **Source Control:** Watch the "Source Control" tab in VS Code. The agents will create new branches (`feat/task-...` or `fix/task-...`) as they work.
*   **GitHub/GitLab:** The agents will open Pull Requests for review. This is the best place to see the code they are producing and the review comments from the `Tech Lead` and `QA Engineer` agents.
*   **File System:** If the agents get stuck, they may create files like `NEEDS_ASSISTANCE.md`. The `Emergency` agent is designed to handle this automatically, but its presence is a sign of a difficult problem.