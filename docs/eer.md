# Genricycle EER Diagram (Mermaid)

```mermaid
erDiagram
    USERS ||--o{ ADDRESSES : has
    USERS ||--o{ ORDERS : places
    USERS ||--o{ TRANSACTIONS : makes
    USERS ||--o{ APPOINTMENTS : books
    USERS ||--o{ LAB_ORDERS : schedules
    USERS ||--o| REWARD_POINTS : has

    CATEGORIES ||--o{ MEDICINES : groups
    ORDERS ||--o{ ORDER_ITEMS : contains
    MEDICINES ||--o{ ORDER_ITEMS : referenced

    DOCTORS ||--o{ APPOINTMENTS : conducts
    LABS ||--o{ LAB_TESTS : offers
    LAB_TESTS ||--o{ LAB_ORDERS : ordered

    USERS {
        int id PK
        string name
        string email
        string phone
        string role
        datetime created_at
    }
    ADDRESSES {
        int id PK
        int user_id FK
        string line1
        string city
        string pincode
        bool is_default
    }
    CATEGORIES {
        int id PK
        string name
    }
    MEDICINES {
        int id PK
        string slug
        string name
        string generic_name
        string brand
        string description
        decimal price
        int stock
        int category_id FK
        string image_url
        datetime created_at
    }
    ORDERS {
        int id PK
        int user_id FK
        string status
        decimal total_amount
        datetime created_at
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
        datetime created_at
    }
    REWARD_POINTS {
        int id PK
        int user_id FK
        int points_balance
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
        int lab_id FK
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
        datetime created_at
    }
```