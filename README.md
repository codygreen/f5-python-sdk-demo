# f5-python-sdk-demo
Demo of how to use the F5 Python SDK to configure a BIG-IP

# Requirements
This demo requires:
- Python3
- [F5 SDK](https://clouddocs.f5.com/sdk/f5-sdk-python/quickstart/) to communicate with the BIG-IP

# Installation
```bash
sudo pip3 install f5-sdk-python
```

# Running the Demo
```bash
export bigipPassword="yourpassword"
python3 bigip.py data.yml
```