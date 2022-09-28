how to run script?
1. https://my.telegram.org/auth?to=apps
2. copy api_id and api_hash to config.py file
3. put a message in config.py
4. ```shell
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 main.py
    ```