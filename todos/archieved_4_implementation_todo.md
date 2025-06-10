Of course. Here is a new, highly detailed `implementation_todo.md` file designed to configure the project for local development with a proxy.

The plan is structured with extreme simplicity and clarity, making it ideal for an autonomous 4B LLM agent to execute flawlessly. Each step is an atomic, verifiable action.

---
Here is the content for the new file:

# `implementation_todo.md` - Local Proxy Configuration

**Project Goal:** To create the necessary configuration files and update existing ones to allow the entire application to be run locally via Docker Compose through an HTTP/HTTPS proxy.

**Guiding Principle:** Complete each task in the exact order it is presented. Verify each step before proceeding to the next.

---

## Feature 1: Create Proxy Environment Configuration

**Goal:** Establish a dedicated environment file for proxy settings.

*   `[x]` **F1.1: Create the proxy environment example file**
    *   **File:** `ai_dev_bot_platform/.env.example.proxy` (Create this new file)
    *   **Action:** Add the following content to the new file. This file will serve as a template for users who need a proxy.
        ```env
        # Proxy Settings
        # Fill these with your corporate or local proxy server details.
        # Example: http://proxy.example.com:8080
        HTTP_PROXY=http://your_proxy_ip:port
        HTTPS_PROXY=http://your_proxy_ip:port

        # Comma-separated list of hostnames that should NOT go through the proxy.
        # This is crucial for letting the 'app' container talk to 'postgres' and 'redis' directly.
        NO_PROXY=localhost,127.0.0.1,postgres,redis
        ```
    *   **Verification:** The new file `.env.example.proxy` exists in the `ai_dev_bot_platform` directory and contains the specified content.

---

## Feature 2: Update Dockerfile to Use Proxy Settings

**Goal:** Modify the `Dockerfile` to accept and use the proxy environment variables during the image build process.

*   `[x]` **F2.1: Add ARG and ENV instructions to the Dockerfile**
    *   **File:** `ai_dev_bot_platform/Dockerfile`
    *   **Action:** Locate the `ENV PYTHONUNBUFFERED=1` line. Insert the following block of code directly after it. This tells Docker to expect proxy arguments during the build and to set them as environment variables inside the container.
        ```dockerfile
        # Set up proxy arguments
        ARG HTTP_PROXY
        ARG HTTPS_PROXY
        ARG NO_PROXY

        # Set proxy environment variables
        ENV HTTP_PROXY=$HTTP_PROXY
        ENV HTTPS_PROXY=$HTTPS_PROXY
        ENV NO_PROXY=$NO_PROXY
        ```
    *   **Verification:** The `Dockerfile` now contains the `ARG` and `ENV` instructions for `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`.

---

## Feature 3: Create a Dedicated Docker Compose File for Proxy Setup

**Goal:** Create a new Docker Compose file that injects the proxy settings into the application container during build and at runtime.

*   `[x]` **F3.1: Create the `docker-compose.proxy.yml` file**
    *   **File:** `ai_dev_bot_platform/docker-compose.proxy.yml` (Create this new file)
    *   **Action:** Add the following content. This file will be used *in addition* to the main `docker-compose.yml` to add the proxy configuration.
        ```yaml
        version: '3.8'

        # This file is an overlay for the main docker-compose.yml.
        # It adds proxy configuration to the 'app' service.
        # To use it, run: docker-compose -f docker-compose.yml -f docker-compose.proxy.yml up

        services:
          app:
            # Pass proxy settings to the Docker build process for 'pip install'
            build:
              args:
                - HTTP_PROXY=${HTTP_PROXY}
                - HTTPS_PROXY=${HTTPS_PROXY}
                - NO_PROXY=${NO_PROXY}
            # Pass proxy settings to the running container for runtime requests (e.g., to LLM APIs)
            environment:
              - HTTP_PROXY=${HTTP_PROXY}
              - HTTPS_PROXY=${HTTPS_PROXY}
              - NO_PROXY=${NO_PROXY}
            # Load the proxy settings from a dedicated .env.proxy file
            env_file:
              - .env.proxy
        ```
    *   **Verification:** The new file `docker-compose.proxy.yml` exists in the `ai_dev_bot_platform` directory and contains the specified YAML content.

---

## Feature 4: Document the New Proxy Setup

**Goal:** Update the main `README.md` file with clear instructions on how to use the new proxy development flow.

*   `[x]` **F4.1: Add "Running with a Proxy" section to README.md**
    *   **File:** `README.md`
    *   **Action:** Find the "🚀 Running Locally" section. At the very end of this section, add a new subsection with the following content:
        ```markdown
        ### Running with a Proxy

        If you are behind a corporate or local proxy, follow these steps instead of the standard `docker-compose up`.

        1.  **Create a Proxy Environment File:** Copy the proxy environment template.
            ```bash
            cp ai_dev_bot_platform/.env.example.proxy ai_dev_bot_platform/.env.proxy
            ```

        2.  **Edit `.env.proxy`:** Open the new `ai_dev_bot_platform/.env.proxy` file and fill in your `HTTP_PROXY` and `HTTPS_PROXY` details.

        3.  **Build and Run with Proxy Config:** Use both `docker-compose.yml` and `docker-compose.proxy.yml` files. The `-f` flag allows you to specify multiple files, which are merged together.
            ```bash
            docker-compose -f ai_dev_bot_platform/docker-compose.yml -f ai_dev_bot_platform/docker-compose.proxy.yml up -d --build
            ```
            This will start all services (app, postgres, redis) and correctly inject your proxy settings into the `app` container for both the build process and runtime.

        4.  **Apply Migrations:** This step is the same. Run migrations inside the running `app` container:
            ```bash
            docker-compose -f ai_dev_bot_platform/docker-compose.yml -f ai_dev_bot_platform/docker-compose.proxy.yml exec app alembic upgrade head
            ```
        ```
    *   **Verification:** The `README.md` file now contains the new "Running with a Proxy" section with the correct instructions and commands.