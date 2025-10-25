### 📄 `DEPLOYMENT.md`

# 🚀 Deployment Details

## 🌍 Live Links

-   **Base API:** [https://talent-bridge-api.vercel.app/api/v1/](https://talent-bridge-api.vercel.app/api/v1/)
    
-   **Swagger Documentation:** [https://talent-bridge-api.vercel.app/swagger/](https://talent-bridge-api.vercel.app/swagger/)
    

---

## 👤 Demo Accounts

| Role | Email | Password |
| --- | --- | --- |
| Admin | `admin1@example.com` | `Admin123` |
| Employer | `employer1@example.com` | `Employer123` |
| Job Seeker | `seeker1@example.com` | `Seeker123` |

Use these credentials to log in and explore the API in Swagger or Postman.

---

## 🧩 API Headers

When calling secure endpoints, include:

```makefile
Authorization: Bearer <your_token>
```

Tokens can be obtained via:

```bash
POST /accounts/login/
```

---

## 🧠 Notes

-   Hosted on **Vercel**
    
-   Backend powered by **Django + DRF + Djoser (JWT)**
    
-   Database: **PostgreSQL (Production)**
    
-   Payments: **SSLCommerz Sandbox (Configured)**
    
-   Version: `v1` (Base URL: `/api/v1/`)
    

---