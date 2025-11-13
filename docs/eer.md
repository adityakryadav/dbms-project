# Genricycle Database EER and Schema Details

```mermaid
erDiagram
    USERS ||--o{ ADDRESSES : has
    USERS ||--o{ ORDERS : places
    USERS ||--o{ TRANSACTIONS : makes
    USERS ||--o{ APPOINTMENTS : books
    USERS ||--o{ LAB_ORDERS : schedules
    USERS ||--o| REWARD_POINTS : has_one

    CATEGORIES ||--o{ MEDICINES : groups
    ORDERS ||--o{ ORDER_ITEMS : contains
    MEDICINES ||--o{ ORDER_ITEMS : referenced

    DOCTORS ||--o{ APPOINTMENTS : conducts
    LABS ||--o{ LAB_TESTS : offers
    LAB_TESTS ||--o{ LAB_ORDERS : ordered

    USERS {
        int id PK
        string name
        string email UNIQUE
        string phone
        string role DEFAULT "customer"
        string language
        string currency
        string password_hash
        datetime created_at DEFAULT now
    }
    ADDRESSES {
        int id PK
        int user_id FK
        string line1
        string city
        string pincode
        bool is_default DEFAULT 0
    }
    CATEGORIES {
        int id PK
        string name UNIQUE
    }
    MEDICINES {
        int id PK
        string slug
        string name
        string generic_name
        string brand
        string description
        decimal price
        int stock DEFAULT 0
        int category_id FK NULL
        string image_url
        datetime created_at DEFAULT now
    }
    ORDERS {
        int id PK
        int user_id FK
        string status DEFAULT "pending"
        decimal total_amount DEFAULT 0
        datetime created_at DEFAULT now
    }
    ORDER_ITEMS {
        int id PK
        int order_id FK
        int medicine_id FK
        int quantity
        decimal price
    }
    TRANSACTIONS {
        int id PK
        int user_id FK
        int order_id FK NULL
        string type
        decimal amount
        string status
        datetime created_at DEFAULT now
    }
    REWARD_POINTS {
        int id PK
        int user_id FK UNIQUE
        int points_balance DEFAULT 0
        datetime updated_at
    }
    DOCTORS {
        int id PK
        string name
        string specialty
        int experience_years
        decimal consultation_fee
        string image_url
    }
    APPOINTMENTS {
        int id PK
        int user_id FK
        int doctor_id FK
        datetime scheduled_at
        string status
    }
    LABS {
        int id PK
        string name
        string city
        string contact
    }
    LAB_TESTS {
        int id PK
        string name
        string category
        decimal price
        int lab_id FK NULL
    }
    LAB_ORDERS {
        int id PK
        int user_id FK
        int lab_test_id FK
        datetime scheduled_at
        string status
    }
    RECYCLE_REQUESTS {
        int id PK
        string facility_name
        string phone
        string address
        string city
        string pincode
        string status
        datetime created_at DEFAULT now
    }
```

---

## Schema Constraints and Relationships

- Users
  - `email` is `UNIQUE`.
  - `role` defaults to `customer`.
  - Optional profile fields: `language`, `currency`.
  - `password_hash` stores a hashed password for authentication.

- Addresses
  - `user_id` references `users(id)` with `ON DELETE CASCADE`.
  - `is_default` is an integer flag (0/1), default `0`.

- Categories and Medicines
  - `categories.name` is `UNIQUE`.
  - `medicines.category_id` references `categories(id)` with `ON DELETE SET NULL`.
  - `medicines.price` is required; `stock` defaults to `0`.

- Orders and Order Items
  - `orders.user_id` references `users(id)` with `ON DELETE CASCADE`.
  - `order_items.order_id` references `orders(id)` with `ON DELETE CASCADE`.
  - `order_items.medicine_id` references `medicines(id)` with `ON DELETE CASCADE`.

- Transactions
  - `transactions.user_id` references `users(id)` with `ON DELETE CASCADE`.
  - `transactions.order_id` optionally references `orders(id)` with `ON DELETE SET NULL`.

- Reward Points
  - `reward_points.user_id` is `UNIQUE`, enforcing a strict 1:1 relationship with `users`.

- Doctors and Appointments
  - `appointments.user_id` references `users(id)` with `ON DELETE CASCADE`.
  - `appointments.doctor_id` references `doctors(id)` with `ON DELETE CASCADE`.

- Labs, Lab Tests, Lab Orders
  - `lab_tests.lab_id` references `labs(id)` with `ON DELETE SET NULL`.
  - `lab_orders.user_id` references `users(id)` with `ON DELETE CASCADE`.
  - `lab_orders.lab_test_id` references `lab_tests(id)` with `ON DELETE CASCADE`.

- Recycle Requests
  - Independent entity used to track recycle facility intakes; no foreign keys.

---

## Notes on Persistence and Auth

- The application uses SQLite at `storage/genricycle.db` with `PRAGMA foreign_keys = ON`.
- Previously, login/signup only set `localStorage` and did not persist to DB. The new `/api/auth/signup` and `/api/auth/login` endpoints persist and verify users against the `users` table, ensuring retention across sessions.