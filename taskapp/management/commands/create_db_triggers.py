from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = "Создает триггеры и функции в базе данных"

    def handle(self, *args, **options):
        sql_statements = [

            # 1.1. Триггер на создание напоминания при добавлении задачи
            """
            CREATE OR REPLACE FUNCTION create_reminder_on_task_insert()
            RETURNS TRIGGER AS $$
            BEGIN
                INSERT INTO Reminder (task_id, date_of_remind, type_of_remind)
                VALUES (NEW.task_id, NOW() + INTERVAL '1 day', 'Push');
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER trg_create_reminder
            AFTER INSERT ON Task
            FOR EACH ROW
            EXECUTE FUNCTION create_reminder_on_task_insert();
            """,

            # 1.2. Триггер для обновления даты изменения задачи
            """
            CREATE OR REPLACE FUNCTION update_task_last_modified()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.task_make_date = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER trg_update_task_time
            BEFORE UPDATE ON Task
            FOR EACH ROW
            EXECUTE FUNCTION update_task_last_modified();
            """,

            # 1.3. Триггер для предотвращения удаления незавершенных задач
            """
            CREATE OR REPLACE FUNCTION prevent_deleting_completed_tasks()
            RETURNS TRIGGER AS $$
            BEGIN
                IF OLD.task_status = 'В работе' THEN
                    RAISE EXCEPTION 'Нельзя удалить незавершенную задачу';
                END IF;
                RETURN OLD;
            END;
            $$ LANGUAGE plpgsql;

            CREATE TRIGGER trg_prevent_delete_task
            BEFORE DELETE ON Task
            FOR EACH ROW
            EXECUTE FUNCTION prevent_deleting_completed_tasks();
            """,

            # Создание представления
            """
            CREATE OR REPLACE VIEW task_summary_view AS
            SELECT t.task_id, t.task_name, t.task_status, p.project_name
            FROM Task t
            LEFT JOIN Project p ON t.project_id = p.project_id;
            """,

            # Регистрация нового пользователя
            """
                CREATE OR REPLACE FUNCTION register_user(
                p_user_name VARCHAR,
                p_user_surname VARCHAR,
                p_user_email VARCHAR,
                p_user_login VARCHAR,
                p_user_password VARCHAR
            )
            RETURNS TEXT AS $$
            BEGIN
                -- Проверяем, есть ли уже такой email или логин
                IF EXISTS (SELECT 1 FROM TaskMaker_User WHERE user_email = p_user_email OR user_login = p_user_login) THEN
                    RETURN 'Ошибка: Пользователь с таким email или логином уже существует';
                END IF;

                -- Хешируем пароль (используем bcrypt)
                INSERT INTO TaskMaker_User (user_name, user_surname, user_email, user_login, user_password)
                VALUES (p_user_name, p_user_surname, p_user_email, p_user_login, crypt(p_user_password, gen_salt('bf')));

                -- Создание пользователя в PostgreSQL
                EXECUTE format('CREATE USER %I WITH PASSWORD %L', p_user_login, p_user_password);

                -- Назначаем роль project_user
                EXECUTE format('GRANT project_user TO %I', p_user_login);

                RETURN 'Пользователь успешно зарегистрирован';
            END;
            $$ LANGUAGE plpgsql;
            """
        ]

        with connection.cursor() as cursor:
            for sql in sql_statements:
                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS("Команда выполнена успешно."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Ошибка выполнения SQL: {e}"))