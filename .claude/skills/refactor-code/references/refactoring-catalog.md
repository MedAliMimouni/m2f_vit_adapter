# Refactoring Catalog

A practical reference of common refactoring patterns with when to use them, before/after examples, and risk levels.

---

## 1. Extract Function

**When to use:** A code fragment can be grouped together, a function is too long, or a comment explains what a block does.

**Risk:** Low

```python
# Before
def process_order(order):
    # validate order
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Negative total")
    # ... rest of processing

# After
def validate_order(order):
    if not order.items:
        raise ValueError("Empty order")
    if order.total < 0:
        raise ValueError("Negative total")

def process_order(order):
    validate_order(order)
    # ... rest of processing
```

---

## 2. Rename (Variable / Function / Class)

**When to use:** A name does not clearly communicate its purpose, or uses abbreviations that are not universally understood.

**Risk:** Low (internal), Medium (public API)

```python
# Before
def calc(d, r):
    return d * r * 0.01

# After
def calculate_discount(price, rate_percent):
    return price * rate_percent * 0.01
```

---

## 3. Extract Variable

**When to use:** A complex expression is hard to understand, or the same expression is used multiple times.

**Risk:** Low

```python
# Before
if user.age >= 18 and user.country in ALLOWED_COUNTRIES and user.verified:
    grant_access(user)

# After
is_adult = user.age >= 18
is_allowed_country = user.country in ALLOWED_COUNTRIES
is_eligible = is_adult and is_allowed_country and user.verified
if is_eligible:
    grant_access(user)
```

---

## 4. Inline (Variable / Function)

**When to use:** A variable or function adds no clarity beyond what the expression itself provides, or is used only once with a trivial body.

**Risk:** Low

```python
# Before
def is_eligible(user):
    return user.active

eligible = is_eligible(user)
if eligible:
    process(user)

# After
if user.active:
    process(user)
```

---

## 5. Move (Function / Field / Class)

**When to use:** A function or class is in the wrong module, or is used more by another module than the one it lives in.

**Risk:** Medium — requires updating all import sites.

```python
# Before: utils.py contains format_currency used only by billing module
# utils.py
def format_currency(amount): ...

# After: moved to billing/formatting.py
# billing/formatting.py
def format_currency(amount): ...
```

---

## 6. Split Loop

**When to use:** A single loop does two or more distinct tasks that could be separated for clarity and independent testability.

**Risk:** Low (may have minor performance impact on very large datasets; usually negligible)

```python
# Before
totals = []
names = []
for item in items:
    totals.append(item.price * item.qty)
    names.append(item.name.upper())

# After
totals = [item.price * item.qty for item in items]
names = [item.name.upper() for item in items]
```

---

## 7. Replace Conditional with Polymorphism

**When to use:** A switch or chain of if/elif checks a type field to decide behavior. Each branch has distinct logic that belongs with its type.

**Risk:** High — restructures class hierarchy; affects many files.

```python
# Before
def calculate_area(shape):
    if shape.type == "circle":
        return math.pi * shape.radius ** 2
    elif shape.type == "rectangle":
        return shape.width * shape.height

# After
class Circle:
    def area(self):
        return math.pi * self.radius ** 2

class Rectangle:
    def area(self):
        return self.width * self.height
```

---

## 8. Extract Class

**When to use:** A class is doing too much (violates Single Responsibility Principle), or a group of fields and methods clearly belong together as their own concept.

**Risk:** Medium — changes class interfaces; may require updating consumers.

```python
# Before
class Order:
    def __init__(self):
        self.items = []
        self.customer_name = ""
        self.customer_email = ""
        self.customer_phone = ""

    def get_customer_contact(self): ...
    def validate_customer(self): ...
    def calculate_total(self): ...

# After
class Customer:
    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone

    def get_contact(self): ...
    def validate(self): ...

class Order:
    def __init__(self, customer):
        self.items = []
        self.customer = customer

    def calculate_total(self): ...
```

---

## 9. Introduce Parameter Object

**When to use:** Multiple functions pass the same group of parameters together, or a function has too many parameters.

**Risk:** Medium — changes function signatures; requires updating all callers.

```python
# Before
def create_event(title, start_date, end_date, start_time, end_time):
    ...

def validate_event(start_date, end_date, start_time, end_time):
    ...

# After
@dataclass
class TimeRange:
    start_date: date
    end_date: date
    start_time: time
    end_time: time

def create_event(title, time_range: TimeRange):
    ...

def validate_event(time_range: TimeRange):
    ...
```

---

## 10. Replace Magic Number with Named Constant

**When to use:** A literal number (or string) appears in code without explanation, or the same literal is used in multiple places.

**Risk:** Low

```python
# Before
def calculate_shipping(weight):
    if weight > 50:
        return weight * 0.15
    return weight * 0.10

# After
MAX_STANDARD_WEIGHT_KG = 50
HEAVY_RATE_PER_KG = 0.15
STANDARD_RATE_PER_KG = 0.10

def calculate_shipping(weight):
    if weight > MAX_STANDARD_WEIGHT_KG:
        return weight * HEAVY_RATE_PER_KG
    return weight * STANDARD_RATE_PER_KG
```
