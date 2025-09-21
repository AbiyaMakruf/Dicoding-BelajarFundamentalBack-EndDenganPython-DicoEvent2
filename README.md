# Proyek Pertama: Dico Event 1
## Penilaian Proyek
Proyek ini berhasil mendapatkan bintang 5/5 pada submission dicoding course Belajar Fundamental Back-End Dengan Python.

![Penilaian Proyek](README/penilaian_proyek.png)


# DicoEvent

RESTful API untuk manajemen **event, ticket, registration, dan payment** menggunakan Django REST Framework + PostgreSQL.
Proyek ini dibuat untuk memenuhi submission dengan target nilai **Advanced (4 pts)**.

---

# Starter

1. Aktifkan virtual environment:

   ```bash
   pipenv shell
   ```

2. Install dependency:

   ```bash
   pipenv install django==4.2 djangorestframework psycopg2-binary python-decouple djangorestframework-simplejwt django-filter
   ```

3. Buat project Django:

   ```bash
   django-admin startproject DicoEvent .
   ```

4. Buat database PostgreSQL:

   ```sql
   psql -U postgres
   CREATE DATABASE dico_event;
   GRANT ALL PRIVILEGES ON DATABASE "dico_event" TO developer;
   ALTER DATABASE "dico_event" OWNER TO developer;
   ```

5. Buat file `.env` di root project:

   ```env
   DATABASE_NAME=dico_event
   DATABASE_USER=developer
   DATABASE_PASSWORD=your_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   SECRET_KEY=django-insecure-ganti-dengan-yang-aman
   DEBUG=True
   ```

6. Migrasi awal:

   ```bash
   python manage.py migrate
   ```

---

# Ketentuan Project

## Pengantar

Setiap kriteria dapat bernilai **0 sampai 4 points (pts)**.
Untuk lulus, minimal **2 points per kriteria**. Submission ditolak jika ada kriteria dengan **0 points**.

---

## Kriteria 1: Menggunakan Database untuk Menyimpan Data

### Reject (0 pts)

* Data tidak disimpan di database apa pun.
* Tidak ada konfigurasi database atau konfigurasi yang salah.
* Menggunakan database selain PostgreSQL.
* Terdapat error dalam pengujian mandatory Postman.

### Basic (2 pts)

* Data berhasil disimpan di PostgreSQL.
* Menggunakan Django ORM dasar (CRUD).
* Semua pengujian mandatory Postman tidak error.

### Skilled (3 pts)

* Memenuhi ketentuan sebelumnya.
* Database dinormalisasi, ada relasi antar tabel.
* Terdapat ERD dengan nama `ERD-DicoEvent-versi-1.png`.
* Ada unique constraint, misalnya pada field **email** di tabel users.

### Advanced (4 pts)

* Memenuhi ketentuan sebelumnya.
* Kredensial database disimpan di **environment variables** (`DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`).
* Menggunakan Django ORM lanjutan: **limit, ordering, filter**.
* Menggunakan UUID sebagai primary key.
* Semua pengujian Postman (mandatory & optional) lolos tanpa error.

---

## Kriteria 2: Menerapkan Autentikasi dan Otorisasi pada RESTful API Django

### Reject (0 pts)

* Tidak ada autentikasi/otorisasi.
* Menggunakan session/cookies (salah metode).
* Tidak ada RBAC.
* Terdapat error dalam pengujian mandatory Postman.

### Basic (2 pts)

* Implementasi autentikasi JWT.
* RBAC role dasar: **user**, **admin**, **superuser**.

  * **Superuser**: akses penuh.
  * **Admin**: CRUD Event, Ticket, Registration, Payment.
  * **User**: daftar/login, lihat Event & Ticket, CRUD Registration & Payment (hanya miliknya).
* Semua pengujian mandatory Postman tidak error.

### Skilled (3 pts)

* Memenuhi ketentuan sebelumnya.
* JWT Access Token berlaku **3 jam**.
* JWT diatur sebagai default authentication di `settings.py`.

### Advanced (4 pts)

* Memenuhi ketentuan sebelumnya.
* Membuat **custom User model**.
* RBAC mencakup role tambahan **organizer**:

  * Organizer hanya bisa kelola event miliknya.
* Ada **custom permission** di views.
* Semua pengujian Postman (mandatory & optional) lolos tanpa error.

---

# Tips Menjalankan Project

1. **Run server**

   ```bash
   python manage.py runserver
   ```

2. **Buat superuser**

   ```bash
   python manage.py createsuperuser
   ```

3. **Testing API**

   * Import file Postman dari folder `postman/`.
   * Gunakan environment `[788] DicoEvent.postman_environment.json`.
   * Jalankan semua test (mandatory & optional).

4. **ERD**

   * Simpan file ERD di root project dengan nama `ERD-DicoEvent-versi-1.png`.

---

# Tips Maintenance & Truncate

Kadang perlu reset data agar tidak bentrok saat testing ulang. Pilihan:

### Truncate Semua Data

```bash
python manage.py flush
```

* Menghapus semua data termasuk superuser.
* Migrasi tetap ada.

### Hapus Semua Data Kecuali Superuser

Masuk Django shell:

```bash
python manage.py shell
```

Lalu jalankan:

```python
from users.models import User
from events.models import Event, Ticket, Registration, Payment

# hapus semua user kecuali superuser
User.objects.exclude(is_superuser=True).delete()

# hapus semua data event dkk
Event.objects.all().delete()
Ticket.objects.all().delete()
Registration.objects.all().delete()
Payment.objects.all().delete()
```

### Drop Database (reset total)

Jika migrasi rusak:

```sql
DROP DATABASE dico_event;
CREATE DATABASE dico_event;
GRANT ALL PRIVILEGES ON DATABASE dico_event TO developer;
ALTER DATABASE dico_event OWNER TO developer;
```

Lalu migrate ulang:

```bash
python manage.py migrate
```

---

# Pengujian

* Koleksi Postman tersedia di folder `postman/`.
* Gunakan environment `[788] DicoEvent.postman_environment.json`.
* Semua test **mandatory & optional** harus **PASS** untuk mendapat nilai Advanced.

---
