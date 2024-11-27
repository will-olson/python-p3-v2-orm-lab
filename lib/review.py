from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        if not self.is_valid_employee_id(value):
            raise ValueError("Employee ID does not exist.")
        self._employee_id = value

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
            sql = "INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)"
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self


    @classmethod
    def create(cls, year, summary, employee_id):
        if not isinstance(year, int):
            raise ValueError("Year must be an integer.")
        if year < 2000:
            raise ValueError("Year must be 2000 or later.")

        if not isinstance(summary, str) or len(summary) == 0:
            raise ValueError("Summary must be a non-empty string.")

        if not cls.is_valid_employee_id(employee_id):
            raise ValueError("Employee ID does not exist.")

        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def is_valid_employee_id(cls, employee_id):
        sql = "SELECT id FROM employees WHERE id = ?"
        CURSOR.execute(sql, (employee_id,))
        return CURSOR.fetchone() is not None

    @classmethod
    def instance_from_db(cls, row):
        id, year, summary, employee_id = row
        return cls(year, summary, employee_id, id)
   
    @classmethod
    def find_by_id(cls, id):
        sql = "SELECT * FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
       if self.id is not None:
            sql = "UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?"
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    def delete(self):
       if self.id is not None:
            sql = "DELETE FROM reviews WHERE id = ?"
            CURSOR.execute(sql, (self.id,))
            CONN.commit()
            del Review.all[self.id]
            self.id = None

    @classmethod
    def get_all(cls):
        sql = "SELECT * FROM reviews"
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

