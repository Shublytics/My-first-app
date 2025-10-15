from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = "students.json"

# ---------------- Utility Functions ----------------
def read_data():
    """Read student data from JSON file. If file is empty, return empty dict."""
    if not os.path.exists(DATA_FILE):
        return {}
    try:
        with open(DATA_FILE, "r") as file:
            content = file.read().strip()
            if not content:  # Empty file
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        return {}

def write_data(data):
    """Write updated student data to JSON file"""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# ---------------- GET All or Filtered Students ----------------
@app.route('/students', methods=['GET'])
def get_students():
    """
    GET /students               -> Returns all students
    GET /students?course=XYZ    -> Returns students filtered by course
    """
    students = read_data()
    course = request.args.get('course')  # Query parameter
    if course:
        filtered = {id: s for id, s in students.items() if s.get('course') == course}
        return jsonify(filtered)
    return jsonify(students)

# ---------------- GET Student by ID (Path Parameter) ----------------
@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    """
    GET /students/<id> -> Returns the student with given ID
    """
    students = read_data()
    student = students.get(student_id)
    if not student:
        return jsonify({"error": "Student not found"}), 404
    return jsonify(student)

# ---------------- POST: Add New Student ----------------
@app.route('/students', methods=['POST'])
def add_student():
    students = read_data()
    new_student = request.get_json()
    new_id = str(max(map(int, students.keys()), default=0) + 1)
    students[new_id] = new_student
    write_data(students)
    return jsonify({"message": "Student added", "id": new_id}), 201

# ---------------- PUT: Replace Existing Student ----------------
@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    students = read_data()
    if student_id not in students:
        return jsonify({"error": "Student not found"}), 404
    students[student_id] = request.get_json()
    write_data(students)
    return jsonify({"message": "Student updated", "data": students[student_id]})

# ---------------- DELETE: Remove Student ----------------
@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    students = read_data()
    if student_id not in students:
        return jsonify({"error": "Student not found"}), 404
    del students[student_id]
    write_data(students)
    return jsonify({"message": f"Student {student_id} deleted"})

@app.route('/')
def home():
    return render_template('welcome.html')

# ---------------- Run Flask App ----------------
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
