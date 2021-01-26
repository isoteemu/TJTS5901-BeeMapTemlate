# Setting up config file for secrets and stuff

Flask quickstart:
<https://flask.palletsprojects.com/en/1.1.x/config/>

## Setup

1. Create default config file `default_config.py`. In this file you can put default values that should be shared between environments - build, testing, development, production.

    ```python
    JSON_AS_ASCII = False
    OUR_TEAM_APP_NAME = "Super awesome beehive locator 3000"
    ```

2. Create instance specific configuration `instance_config.py` for your development environment. Good practice would be to store instance files out-of-tree, but for sake of simplicity lets just keep it under project. This file **will be overridden by pipeline**.

    ```python
    SECRET_KEY = "I never tell."
    DEBUG = True
    ```

3. Add `instance_config.py` into `.gitignore`

4. Add config loading into application, after `Flask()` object has been initialized:

    ```python
    app = Flask(__name__)

    # Load configs
    app.config.from_pyfile("default_config.py")
    # silent param allows missing config files.
    app.config.from_pyfile("instance_config.py", silent=True)
    ```

5. In [gitlab](gitlab.jyu.fi/), navigate under you project, and add instance config as protected variable.
    - Go into **Settings** → **CI / CD** and click Variables **[ EXPAND ]**
    - Click on **[ Add variable ]**
    - Define instance config:
      - **Key**: `INSTANCE_CONFIG_PRODUCTION`
      - **Value**:
        ```
        SECRET_KEY = "your own secret here"
        ENV = "production"
        DEBUG = False
        ```
      - **Type**: File  
      - **Protected variable**: Yes
    - Save by clicking **[ Add Variable ]**

6: Setup pipeline to copy config file into deployment.
  - Edit `.gitlab-ci.yml`, and add into `deployment: script:` phase before actual deployment: `cp $INSTANCE_CONFIG_PRODUCTION instance_config.py`.

```yaml
deploy:
    stage: deploy
    environment:
        name: production
    image: google/cloud-sdk:alpine
    script:
    - echo $SERVICE_ACCOUNT > /tmp/$CI_PIPELINE_ID.json
    - echo $GOOGLE_APPLICATION_CREDENTIALS > appcredentials.json
    - gcloud auth activate-service-account --key-file /tmp/$CI_PIPELINE_ID.json
    - cp $INSTANCE_CONFIG_PRODUCTION instance_config.py
    - gcloud --quiet --project $PROJECT_ID app deploy app.yaml
    - rm /tmp/$CI_PIPELINE_ID.json
```


## Things to improve

- For generating secrets worth keeping, see: <https://flask.palletsprojects.com/en/1.1.x/config/#SECRET_KEY>
- Moving config files out-of-tree, or even into a semi-protected `instance/` folder.
- If you have hard coded values, like one in `datastore.Client()`, move it into config variable.
- Add step in testing phase to check if config values are sane.
