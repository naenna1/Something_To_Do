
DROP TABLE IF NOT EXISTS category;

DROP TABLE IF NOT EXISTS task;

CREATE TABLE category(
          id INT PRIMARY KEY,
          name VARCHAR(100),
         description VARCHAR);

CREATE TABLE task(
          id INT PRIMARY KEY ,
          title VARCHAR(100),
          category VARCHAR(100),
          description VARCHAR(200),
          creation_date DATE,
          completed_date DATE,
          due_date DATE);

SELECT* FROM task;

SELECT* FROM category;
