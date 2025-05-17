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
            """,
            """
            CREATE OR REPLACE PROCEDURE assign_task_by_admin(
                IN p_task_id INT,
                IN p_implementer_id INT,
                IN p_admin_id INT,
                OUT result TEXT
            )
            LANGUAGE plpgsql
            AS $$
            DECLARE
                v_is_admin BOOLEAN;
            BEGIN
                -- Проверка, является ли пользователь админом проекта
                SELECT EXISTS (
                    SELECT 1 FROM ProjectMember 
                    WHERE user_id = p_admin_id 
                    AND project_role = 'admin'
                    AND project_id = (SELECT project_id FROM Task WHERE task_id = p_task_id)
                ) INTO v_is_admin;

                IF NOT v_is_admin THEN
                    result := 'Ошибка: Только администратор проекта может назначать исполнителя';
                    RETURN;
                END IF;

                -- Назначение исполнителя
                UPDATE Task SET task_implementer_id = p_implementer_id WHERE task_id = p_task_id;

                result := 'Исполнитель успешно назначен';

            EXCEPTION WHEN OTHERS THEN
                -- обработка любых других ошибок
                result := 'Произошла ошибка при назначении исполнителя';
            END;
            $$;
            BEGIN;
            CALL assign_task_by_admin(1, 2, 3, NULL);
            COMMIT;
                """,
            """
                -- Назначение нового администратора проекта
                CREATE OR REPLACE FUNCTION set_new_project_admin(
                p_project_id INT,
                p_current_admin_id INT,
                p_new_admin_id INT
            )
            RETURNS TEXT AS $$
            DECLARE
                v_is_admin BOOLEAN;
            BEGIN
                -- Проверка, является ли вызывающий пользователь текущим админом
                SELECT EXISTS (
                    SELECT 1 FROM ProjectMember 
                    WHERE user_id = p_current_admin_id 
                    AND project_role = 'admin' 
                    AND project_id = p_project_id
                ) INTO v_is_admin;

                IF NOT v_is_admin THEN
                    RETURN 'Ошибка: Только текущий администратор может назначить нового';
                END IF;

                -- Обновление ролей
                UPDATE ProjectMember
                SET project_role = 'user'
                WHERE project_id = p_project_id AND user_id = p_current_admin_id;

                UPDATE ProjectMember
                SET project_role = 'admin'
                WHERE project_id = p_project_id AND user_id = p_new_admin_id;

                RETURN 'Новый администратор успешно назначен';
            END;
            $$ LANGUAGE plpgsql;

        """,
            """
            -- Функция, запрещающая удаление последнего админа
            CREATE OR REPLACE FUNCTION prevent_admin_removal()
            RETURNS TRIGGER AS $$
            DECLARE
                admin_count INT;
            BEGIN
                SELECT COUNT(*) INTO admin_count 
                FROM ProjectMember 
                WHERE project_id = OLD.project_id AND project_role = 'admin';

                IF OLD.project_role = 'admin' AND admin_count <= 1 THEN
                    RAISE EXCEPTION 'Нельзя удалить последнего администратора проекта';
                END IF;

                RETURN OLD;
            END;
            $$ LANGUAGE plpgsql;
            -- Триггер
            CREATE TRIGGER trg_prevent_admin_delete
            BEFORE DELETE ON ProjectMember
            FOR EACH ROW
            EXECUTE FUNCTION prevent_admin_removal();

            """,
            """CREATE OR REPLACE FUNCTION send_reminder_notifications() 
            RETURNS void AS $$
            DECLARE
                reminder RECORD;
            BEGIN
                FOR reminder IN
                    SELECT * FROM Reminder
                    WHERE date_of_remind <= CURRENT_TIMESTAMP AND type_of_remind IN ('Email', 'Push')
                LOOP
                    -- Отправка уведомлений по Email или Push (в реальной системе это будет интеграция с внешними сервисами)
                    IF reminder.type_of_remind = 'Email' THEN
                        -- Логика отправки email (например, через внешнюю библиотеку или API)
                        RAISE NOTICE 'Отправка email на задачу: %', reminder.task_id;
                    ELSIF reminder.type_of_remind = 'Push' THEN
                        -- Логика отправки push-уведомлений
                        RAISE NOTICE 'Отправка push-уведомления на задачу: %', reminder.task_id;
                    END IF;
                END LOOP;
            END;
            $$ LANGUAGE plpgsql;
            -- Создаем триггер
            CREATE TRIGGER send_reminder_notifications_trigger
            AFTER INSERT OR UPDATE ON Reminder
            FOR EACH ROW
            EXECUTE FUNCTION send_reminder_notifications();
            """,
        ]

        with connection.cursor() as cursor:
            for sql in sql_statements:
                try:
                    cursor.execute(sql)
                    self.stdout.write(self.style.SUCCESS("Команда выполнена успешно."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Ошибка выполнения SQL: {e}"))