from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:rony2025@rony-formulario.cpo2i6842kw2.us-east-1.rds.amazonaws.com:3306/equipos_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mi_clave_secreta_2024'

db = SQLAlchemy(app)

class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    tipo_equipo = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    sistema_operativo = db.Column(db.String(100), nullable=False)
    ram = db.Column(db.String(50), nullable=False)
    almacenamiento = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_mantenimiento = db.Column(db.DateTime)
    estado = db.Column(db.String(50), default='Activo')
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'marca': self.marca,
            'tipo_equipo': self.tipo_equipo,
            'modelo': self.modelo,
            'sistema_operativo': self.sistema_operativo,
            'ram': self.ram,
            'almacenamiento': self.almacenamiento,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_registro else None,
            'fecha_mantenimiento': self.fecha_mantenimiento.strftime('%Y-%m-%d') if self.fecha_mantenimiento else None,
            'estado': self.estado
        }

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/equipos', methods=['GET'])
def get_equipos():
    equipos = Equipo.query.all()
    return jsonify([equipo.to_dict() for equipo in equipos])

@app.route('/api/equipos/<int:id>', methods=['GET'])
def get_equipo(id):
    equipo = Equipo.query.get_or_404(id)
    return jsonify(equipo.to_dict())

@app.route('/api/equipos', methods=['POST'])
def crear_equipo():
    try:
        data = request.json
        nuevo_equipo = Equipo(
            codigo=data['codigo'],
            marca=data['marca'],
            tipo_equipo=data['tipo_equipo'],
            modelo=data['modelo'],
            sistema_operativo=data['sistema_operativo'],
            ram=data['ram'],
            almacenamiento=data['almacenamiento'],
            fecha_mantenimiento=datetime.strptime(data['fecha_mantenimiento'], '%Y-%m-%d') if data.get('fecha_mantenimiento') else None,
            estado=data.get('estado', 'Activo')
        )
        db.session.add(nuevo_equipo)
        db.session.commit()
        return jsonify({'success': True, 'equipo': nuevo_equipo.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/equipos/<int:id>', methods=['PUT'])
def actualizar_equipo(id):
    try:
        equipo = Equipo.query.get_or_404(id)
        data = request.json
        equipo.codigo = data.get('codigo', equipo.codigo)
        equipo.marca = data.get('marca', equipo.marca)
        equipo.tipo_equipo = data.get('tipo_equipo', equipo.tipo_equipo)
        equipo.modelo = data.get('modelo', equipo.modelo)
        equipo.sistema_operativo = data.get('sistema_operativo', equipo.sistema_operativo)
        equipo.ram = data.get('ram', equipo.ram)
        equipo.almacenamiento = data.get('almacenamiento', equipo.almacenamiento)
        equipo.estado = data.get('estado', equipo.estado)
        if data.get('fecha_mantenimiento'):
            equipo.fecha_mantenimiento = datetime.strptime(data['fecha_mantenimiento'], '%Y-%m-%d')
        db.session.commit()
        return jsonify({'success': True, 'equipo': equipo.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/equipos/<int:id>', methods=['DELETE'])
def eliminar_equipo(id):
    try:
        equipo = Equipo.query.get_or_404(id)
        db.session.delete(equipo)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Equipo eliminado correctamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'database': 'connected'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
