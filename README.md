Requirements
------------

- Python >= 3.6.0
- Service account for accessing Google Sheet

Installation
------------

- (optional) create a virtualenv

- Install all required libraries
```bash
pip install -r requirements.txt
```
- Copy then edit configuration
```bash
cp env.sample .env
```

Running
-------

**note: use supervisord for run the script as a daemon (running in background)**

```bash
python main.py
```
