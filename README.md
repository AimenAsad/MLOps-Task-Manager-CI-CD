The primary objective of this assignment was to build a robust, containerized application and establish an automated deployment pipeline. This involved:

* Developing a simple **Task Manager web application** using Flask and MongoDB.
* **Containerizing** the Flask app and MongoDB database using Docker.
* Implementing an automated **CI/CD pipeline** with GitHub Actions for continuous integration and continuous deployment.
* Deploying the entire multi-container application on **Kubernetes (Minikube)**, utilizing ConfigMaps and Secrets for secure and flexible configuration.

---

##  Technologies Used

* **Python 3:** Core programming language.
* **Flask:** Web framework for the application.
* **MongoDB:** NoSQL database for task storage.
* **PyMongo:** Python driver for MongoDB.
* **Docker:** For containerization of the Flask app and MongoDB.
* **Docker Compose:** For local multi-container orchestration.
* **GitHub Actions:** For Continuous Integration and Continuous Deployment (CI/CD).
* **Kubernetes (Minikube):** For container orchestration and local deployment.
* **kubectl:** Kubernetes command-line tool.
* **HTML/CSS (Bootstrap):** For the basic user interface.

---

## Project Structure
'''
├── .github/
│   └── workflows/
│       └── ci-cd.yml             # GitHub Actions workflow definition
├── app/
│   ├── app.py                    # Flask application code
│   ├── requirements.txt          # Python dependencies
│   ├── templates/
│   │   ├── base.html
│   │   ├── home.html             # UI for viewing/adding tasks
│   │   └── index.html
│   └── static/                   # CSS/JS files
├── k8s-manifests/
│   ├── flask-deployment.yaml     # Kubernetes deployment for Flask app
│   ├── flask-service.yaml        # Kubernetes service for Flask app (NodePort)
│   ├── mongodb-deployment.yaml   # Kubernetes deployment for MongoDB
│   ├── mongodb-service.yaml      # Kubernetes service for MongoDB (ClusterIP)
│   ├── configmap.yaml            # Kubernetes ConfigMap for non-sensitive config
│   └── secret.yaml               # Kubernetes Secret for sensitive credentials
├── Dockerfile                    # Dockerfile for the Flask application
├── docker-compose.yml            # Docker Compose file for local setup
└── README.md                     # Project README
'''

---

##  Setup and Deployment Guide

### Prerequisites

Before you begin, ensure you have the following tools installed on your local machine:

* [**Docker Desktop**](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
* [**Minikube**](https://minikube.sigs.k8s.io/docs/start/)
* [**kubectl**](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* [**Git**](https://git-scm.com/downloads)
* A **GitHub account**

### Part 1: Local Application Development & Testing

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
    cd YOUR_REPOSITORY_NAME
    ```
2.  **Navigate to the `app/` directory and install Python dependencies:**
    ```bash
    cd app
    pip install -r requirements.txt
    ```
3.  **Run the Flask application locally (without Docker/MongoDB):**
    * Ensure you have a local MongoDB instance running, or mock the database interactions for testing.
    * Set necessary environment variables (e.g., `MONGO_URI`).
    * `python app.py` (or whatever your main Flask file is).

### Part 2: Containerization with Docker

1.  **Build Docker Images:**
    Navigate to the project root directory where `Dockerfile` and `docker-compose.yml` are located.
    ```bash
    docker-compose build
    ```
2.  **Run Multi-Container Setup Locally:**
    This command will spin up both your Flask application and MongoDB database containers, configured to communicate with each other.
    ```bash
    docker-compose up -d
    ```
3.  **Verify Local Setup:**
    Open your browser and navigate to `http://localhost:5000` (or whatever port your Flask app is exposed on via Docker Compose) to access the Task Manager application.
    
    You can also check container status:
    ```bash
    docker ps
    ```
    To stop and remove containers:
    ```bash
    docker-compose down
    ```

### Part 3: GitHub Actions CI/CD Pipeline

The project implements a robust CI/CD pipeline using GitHub Actions, triggered by specific Git events.

1.  **Branching Strategy:**
    * **`dev` branch:** Used for active development and testing of new features. Pushes to this branch trigger Continuous Integration (CI) checks.
    * **`main` branch:** The stable production branch. Merges into `main` (via Pull Requests) trigger Continuous Deployment (CD).

2.  **Configure GitHub Secrets:**
    Before the CI/CD pipeline can run successfully, you **must** configure the following secrets in your GitHub repository settings (`Settings > Secrets and variables > Actions`):
    * `DOCKER_HUB_USERNAME`
    * `DOCKER_HUB_ACCESS_TOKEN` (Create a Personal Access Token on Docker Hub with push permissions)
    * `FLASK_SECRET_KEY`
    * `MONGO_INITDB_ROOT_USERNAME`
    * `MONGO_INITDB_ROOT_PASSWORD`
    * `KUBE_CONFIG` (Base64 encoded Minikube kubeconfig for remote deployment, if applicable, or for GitHub Actions to interact with your cluster setup. For local Minikube, this might be simplified or handled by local `kubectl` context.)

3.  **CI/CD Workflow (`.github/workflows/ci-cd.yml`):**

    * **Continuous Integration (on `dev` branch push):**
        * Performs Python code linting.
        * Builds Docker images to confirm successful compilation and dependency resolution.

    * **Continuous Deployment (on `main` branch merge via PR):**
        * Re-validates code with linting.
        * Builds and tags Docker images with unique tags (e.g., commit SHA or version).
        * Logs into Docker Hub using secrets.
        * Pushes tagged Docker images to Docker Hub.
        * **Automates Kubernetes deployment updates:**
            * Updates Kubernetes manifest files with the new Docker image tag.
            * Applies the updated manifests to the Kubernetes cluster using `kubectl`.
            * Initiates a rolling restart of the Flask deployment to ensure zero-downtime updates.

    ****

### Part 4: Kubernetes Deployment

This section details how to deploy your multi-container application on a Kubernetes cluster, specifically using Minikube for local development.

1.  **Start Minikube:**
    ```bash
    minikube start
    ```
2.  **Create Kubernetes Manifest Files:**
    The `k8s-manifests/` directory contains all necessary Kubernetes manifest files:
    * `flask-deployment.yaml`: Defines the deployment strategy for the Flask application.
    * `mongodb-deployment.yaml`: Defines the deployment strategy for the MongoDB database.
    * `flask-service.yaml`: Exposes the Flask application externally via a `NodePort` service.
    * `mongodb-service.yaml`: Creates an internal `ClusterIP` service for MongoDB, allowing the Flask app to communicate with it.
    * `configmap.yaml`: Stores **non-sensitive configuration** data, such as MongoDB connection host/port and application debug settings.
        * **Example ConfigMap usage:**
            ```yaml
            # Excerpt from configmap.yaml
            apiVersion: v1
            kind: ConfigMap
            metadata:
              name: app-config
            data:
              mongo-host: "mongodb-service" # Internal K8s service name
              mongo-port: "27017"
              database-name: "taskdb"
              debug-mode: "True"
            ```
    * `secret.yaml`: Securely stores **sensitive information**, such as the Flask Secret Key and MongoDB root username/password.
        * **Example Secret usage (base64 encoded values):**
            ```yaml
            # Excerpt from secret.yaml (values are base64 encoded)
            apiVersion: v1
            kind: Secret
            metadata:
              name: app-secrets
            type: Opaque
            data:
              flask-secret-key: <base64-encoded-flask-secret-key>
              mongo-username: <base64-encoded-mongo-username>
              mongo-password: <base64-encoded-mongo-password>
            ```
            *(Remember to base64 encode your actual values before putting them into `secret.yaml`. Example: `echo -n 'mysecretkey' | base64`)*

3.  **Apply Kubernetes Manifests:**
    Navigate to the project root and apply all manifest files:
    ```bash
    kubectl apply -f k8s-manifests/
    ```
    ****

4.  **Verify Deployment:**
    Check the status of your pods and deployments:
    ```bash
    kubectl get pods
    kubectl get deployments
    kubectl get services
    ```
    Ensure both Flask and MongoDB containers are running (`Running` status).

5.  **Access the Application:**
    Since the Flask service is exposed as a `NodePort`, you can find its accessible URL using Minikube:
    ```bash
    minikube service flask-service --url
    ```
    Open the URL provided in your web browser to access the Task Manager application.

### Container Communication & Config Management

* **Container Communication:**
    The Flask application communicates with the MongoDB database within the Kubernetes cluster using the **`mongodb-service` (ClusterIP)**. Kubernetes' internal DNS allows the Flask pod to resolve `mongodb-service` to the correct internal IP address, facilitating seamless communication between the application and database containers without exposing the database directly outside the cluster.
    ****

* **ConfigMaps and Secrets Utilization:**
    * **ConfigMaps** (`configmap.yaml`) are used for storing **non-sensitive configuration** data like database hostnames (using the internal service name), ports, database names, and debug settings. These values are injected into the Flask application's environment variables.
    * **Secrets** (`secret.yaml`) are used for **securely storing sensitive information** such as the Flask `SECRET_KEY` and MongoDB root username/password. These values are also injected as environment variables into the respective pods, but handled with base64 encoding for basic obfuscation and managed securely by Kubernetes. This separation ensures sensitive data is not exposed in plain text in your configuration files or version control.

---

## Challenges Encountered & Resolutions

* **Challenge 1: Docker Build Caching Issues in CI/CD.**
    * **Resolution:** Implemented multi-stage Docker builds or ensured proper cache invalidation strategies in the GitHub Actions workflow to prevent stale layers.
* **Challenge 2: Environment Variable Propagation to Kubernetes Pods.**
    * **Resolution:** Carefully configured `env` sections in Kubernetes deployment manifests, ensuring correct referencing of `configMapKeyRef` and `secretKeyRef` to pull values from ConfigMaps and Secrets. Debugging involved `kubectl describe pod <pod-name>` to inspect environment variables.
* **Challenge 3: Automated Image Tagging and Manifest Updates in CI/CD.**
    * **Resolution:** Utilized GitHub Actions context (`github.sha` or `github.run_number`) for unique image tagging and a small `bash` script or a specialized GitHub Action to automatically update the image tag in the Kubernetes deployment manifest before applying. This ensures that a new image is always deployed on merge.

---

