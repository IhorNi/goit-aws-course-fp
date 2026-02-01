# Gradio Чат-бот з AWS Bedrock

Розмовний AI чат-бот, побудований на Gradio та LangChain, що використовує AWS Bedrock (модель Mistral), з автентифікацією користувачів через PostgreSQL, розгорнутий на AWS Elastic Beanstalk.

## Огляд проєкту

Цей проєкт демонструє повноцінне розгортання AI-застосунку в хмарі AWS.


## Архітектура

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Internet      │────▶│  ALB (Public)    │────▶│  EB Instances   │
│                 │     │  HTTP/HTTPS      │     │  (Private)      │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                        ┌──────────────────┐              │
                        │  AWS Bedrock     │◀─────────────┤
                        │  (Mistral)       │              │
                        └──────────────────┘              │
                                                          │
                        ┌──────────────────┐              │
                        │  RDS PostgreSQL  │◀─────────────┘
                        │  (Private)       │
                        └──────────────────┘
```

## Функціональність

- **AI Чат-інтерфейс**: Gradio UI зі стрімінгом відповідей
- **Інтеграція AWS Bedrock**: Модель Mistral Large через LangChain
- **Автентифікація користувачів**: PostgreSQL + bcrypt хешування паролів
- **Infrastructure as Code**: Повне розгортання через Terraform
- **Docker**: Контейнеризований застосунок для локальної розробки та продакшену

## Обґрунтування архітектурних рішень

### Чому AWS Elastic Beanstalk?

**Elastic Beanstalk** обрано як керовану платформу (PaaS), яка автоматично забезпечує:

- **Автоматичне масштабування** - система автоматично додає або видаляє інстанси залежно від навантаження (налаштовано на CPU 30-70%)
- **Балансування навантаження** - Application Load Balancer розподіляє трафік між інстансами
- **Моніторинг здоров'я** - автоматичні перевірки стану та заміна несправних інстансів
- **Простота розгортання** - деплой через один скрипт без ручного налаштування серверів
- **Керовані оновлення** - автоматичні оновлення платформи без простоїв

Це дозволяє зосередитися на розробці застосунку, а не на адмініструванні інфраструктури.

### Чому AWS Bedrock?

**AWS Bedrock** обрано як економічно вигідну точку доступу до відкритих AI-моделей:

- **Модель Mistral Large** - потужна open-source модель з хорошим співвідношенням ціна/якість
- **Pay-per-use** - оплата лише за фактичне використання (за токени), без фіксованих витрат
- **Без інфраструктури** - не потрібно розгортати та обслуговувати GPU-сервери
- **Інтеграція з AWS** - нативна інтеграція з IAM, CloudWatch, VPC
- **Масштабованість** - автоматичне масштабування без обмежень

Порівняно з self-hosted рішеннями (наприклад, EC2 з GPU), Bedrock значно дешевший для невеликих та середніх навантажень.

### Чому RDS PostgreSQL?

**Amazon RDS** для керування користувачами обрано з таких причин:

- **Вимога проєкту** - необхідність автентифікації користувачів
- **Керована база даних** - автоматичні бекапи, оновлення, моніторинг
- **Безпека** - розміщення у приватній підмережі, шифрування, Secrets Manager для паролів
- **Надійність** - можливість Multi-AZ для високої доступності
- **PostgreSQL** - надійна, безкоштовна СУБД з великою спільнотою

Для простої автентифікації RDS є оптимальним рішенням, що задовольняє вимоги без надмірної складності.

## Структура проєкту

```
goit-aws-course-fp/
├── app/                          # Python застосунок
│   ├── main.py                   # Точка входу Gradio
│   ├── config.py                 # Конфігурація
│   ├── auth/                     # Модуль автентифікації
│   │   ├── models.py             # SQLAlchemy модель User
│   │   ├── database.py           # З'єднання з БД
│   │   └── auth_handler.py       # Логіка автентифікації
│   ├── chat/                     # Модуль чату
│   │   └── bedrock_client.py     # LangChain + Bedrock
│   └── utils/
│       └── secrets.py            # AWS Secrets Manager
├── tests/                        # Тести
├── docker/
│   ├── Dockerfile
│   └── docker-compose.local.yml
├── terraform/                    # Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│       ├── vpc/                  # Мережа
│       ├── security/             # Security Groups
│       ├── iam/                  # IAM ролі
│       ├── rds/                  # База даних
│       └── elastic_beanstalk/    # EB середовище
├── scripts/
│   ├── deploy.sh                 # Скрипт розгортання
│   ├── destroy.sh                # Скрипт видалення
│   └── init-db.sql               # Ініціалізація БД
├── .ebextensions/
│   └── 01_logging.config
├── Dockerrun.aws.json
└── requirements.txt
```

## Передумови

- Python 3.11+
- Docker та Docker Compose
- AWS CLI з налаштованими credentials
- Terraform 1.5+
- AWS акаунт з доступом до:
  - AWS Bedrock (модель Mistral активована)
  - EC2, RDS, Elastic Beanstalk
  - Secrets Manager, IAM

### Встановлення інструментів

**macOS (Homebrew):**
```bash
# Встановити Homebrew (якщо не встановлено)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Встановити Python
brew install python@3.11

# Встановити Docker Desktop
brew install --cask docker

# Встановити AWS CLI
brew install awscli

# Встановити Terraform
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Перевірити встановлення
python3 --version
docker --version
aws --version
terraform --version
```

**Налаштування AWS CLI:**
```bash
aws configure
# AWS Access Key ID: <ваш ключ>
# AWS Secret Access Key: <ваш секретний ключ>
# Default region: us-east-1
# Default output format: json
```

## Швидкий старт

### Локальна розробка

1. **Клонувати репозиторій**
   ```bash
   git clone <repository-url>
   cd goit-aws-course-fp
   ```

2. **Налаштувати AWS credentials** (для доступу до Bedrock)
   ```bash
   export AWS_ACCESS_KEY_ID=your-access-key
   export AWS_SECRET_ACCESS_KEY=your-secret-key
   export AWS_REGION=us-east-1
   ```

3. **Запустити через Docker Compose**
   ```bash
   docker-compose -f docker/docker-compose.local.yml up --build
   ```

4. **Відкрити застосунок**
   - URL: http://localhost:8080
   - Логін: значення `ADMIN_USERNAME` (за замовчуванням `admin`)
   - Пароль: значення `ADMIN_PASSWORD`

    
## Розгортання в AWS

### 1. Налаштувати Terraform змінні

Створіть файл `terraform/terraform.tfvars`:

```hcl
project_name     = "gradio-chatbot"
environment      = "dev"
aws_region       = "us-east-1"
vpc_cidr         = "10.0.0.0/16"

# RDS
db_instance_class    = "db.t3.micro"
db_allocated_storage = 20
db_multi_az          = false

# Elastic Beanstalk
eb_instance_type  = "t3.small"
eb_min_instances  = 1
eb_max_instances  = 4

# Пароль адміністратора (обов'язково змініть!)
admin_password = "CHANGE_ME"
```

### 2. Розгорнути інфраструктуру

```bash
# Зробити скрипти виконуваними
chmod +x scripts/deploy.sh scripts/destroy.sh

# Розгорнути
./scripts/deploy.sh dev
```

### 3. Доступ до застосунку

Після розгортання буде виведено URL застосунку, схоже на:
```
Application URL: http://gradio-chatbot-dev.us-east-1.elasticbeanstalk.com
```

### 4. Видалення інфраструктури

```bash
./scripts/destroy.sh dev
```

## Конфігурація

### Змінні оточення

| Змінна | Опис | За замовчуванням |
|--------|------|------------------|
| `APP_NAME` | Назва застосунку | `Gradio Chatbot` |
| `APP_HOST` | Хост для прослуховування | `0.0.0.0` |
| `APP_PORT` | Порт застосунку | `8080` |
| `DEBUG` | Режим налагодження | `false` |
| `AUTH_ENABLED` | Увімкнути автентифікацію | `true` |
| `AWS_REGION` | AWS регіон | `us-east-1` |
| `AWS_SECRET_NAME` | Ім'я секрету в Secrets Manager | - |
| `DB_HOST` | Хост PostgreSQL | `localhost` |
| `DB_PORT` | Порт PostgreSQL | `5432` |
| `DB_NAME` | Назва бази даних | `chatbot` |
| `DB_USER` | Користувач БД | `postgres` |
| `ADMIN_USERNAME` | Логін адміністратора | `admin` |
| `ADMIN_PASSWORD` | Пароль адміністратора | - |
| `ADMIN_EMAIL` | Email адміністратора | `admin@example.com` |
| `BEDROCK_MODEL_ID` | ID моделі Bedrock | `mistral.mistral-large-2402-v1:0` |
| `BEDROCK_MAX_TOKENS` | Макс. токенів у відповіді | `1024` |
| `BEDROCK_TEMPERATURE` | Температура моделі | `0.7` |

