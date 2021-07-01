from SPA_app.models import Medicine


def run():
    medicines = Medicine.objects.all()
    medicines.delete()
    print("Medicine table is cleared")
