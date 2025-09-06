PRAGMA foreign_keys = ON;

INSERT INTO books(isbn, title, author, price, stock, created_at) VALUES
  ('9781098166304', 'AI Engineering',' Chip Huyen', 57.74, 5, datetime('now')),
  ('9781098103019', 'Practical MLOps', 'Noah Gift', 58.48, 11, datetime('now')),
  ('9783126071574', 'Netzwerk neu a1', 'Collectif', 26.44, 20, datetime('now')),
  ('9783126071659', 'Netzwerk neu a2', 'Hans Peter & Collectif', 34.95, 10, datetime('now')),
  ('9781285740621', 'Calculus', 'James Stewart', 175.99, 2, datetime('now')),
  ('9780385504218', 'The Da Vinci Code', 'Robert Langdon', 10.00, 8,datetime('now')),
  ('9780135398579', 'Clean Code', 'Robert Martin', 59.99, 6, datetime('now')),
  ('9780135957059', 'The Pragmatic Programmer',' David Thomas & Andrew Hunt', 37.80, 9, datetime('now')),
  ('9798868811340', 'Building Generative AI Agents', 'Tom Taulli & Gaurav Deshmukh', 54.99, 3, datetime('now')),
  ('9781098160296', 'Building Generative AI Services with FastAPI', 'Alireza Parandeh', 54.99, 2, datetime('now'))
ON CONFLICT(isbn) DO UPDATE SET
  title=excluded.title,
  author=excluded.author,
  price=excluded.price
;

INSERT INTO customers(id, name, email) VALUES
  (1, 'Ali Alawiede', 'alialawiedi@icloud.com'),
  (2, 'Deaa Fahed', 'deaafahed@gmail.com'),
  (3, 'Hussein Mahmoud', 'hussein551@gmail.com'),
  (4, 'Aseel Omar', 'aseel77@gamil.com')
ON CONFLICT(id) DO UPDATE SET
  name=excluded.name,
  email=excluded.email
;

INSERT OR IGNORE INTO orders(id, customer_id) VALUES
(1,1),
(2,2),
(3,3);

INSERT OR IGNORE INTO order_items(order_id, isbn, qty) VALUES
(1, '9781098103019',1 ),
(1, '9783126071574', 2),
(2, '9781285740621', 1),
(3, '9781098160296', 1),
(3, '9783126071574', 3);
