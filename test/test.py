def upload(*args, **kwargs):
    for arg in args:
        savedir(arg)
        db.save(arg)

def save_info():
    username = "abc"
    key = "123"
    private_info = {username, key}
    upload(private_info)