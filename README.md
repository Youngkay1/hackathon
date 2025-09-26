# 🚨 Emergency Response USSD System

**Connecting disaster victims to life-saving resources through basic mobile phones**

## 🌍 The Problem

When disasters like floods hit communities in Nigeria, people are often stranded with limited communication options. While smartphones and internet may be unavailable, most people still have basic phones capable of SMS and USSD. This creates a critical gap in emergency response - how do we connect victims to available shelter, food, and transport when traditional communication channels fail?

## 💡 Our Solution

A USSD-based emergency response system that works on any mobile phone, even without internet connectivity. Users simply dial `*123#` and get instant access to:

- 🏠 **Emergency Shelter** - Find available accommodation
- 🍽️ **Food Distribution** - Locate food centers and kitchens  
- 🚗 **Transport Services** - Connect to evacuation and medical transport

## 🔧 How It Works

### For Disaster Victims:
1. **Dial `*123#`** on any mobile phone
2. **Select service type** (1=Shelter, 2=Food, 3=Transport)
3. **Enter location** (e.g., "Lokoja")
4. **Get matched** with nearest available resources
5. **Receive SMS confirmation** with contact details

### For Service Providers:
1. **Register resources** through web dashboard
2. **Update availability** in real-time
3. **Receive SMS alerts** when matched with requests
4. **Coordinate response** directly with victims

## 🏗️ System Architecture

```
📱 Basic Phone (USSD) → 📡 Telecom Gateway → 🖥️ Flask Backend → 🗄️ Database
                                                     ↓
📱 SMS Notifications ← 📡 SMS Gateway ← 🔄 Matching Engine ← 📊 Admin Dashboard
```

### Core Components:

- **USSD Service**: Handles menu navigation and user sessions
- **Matching Engine**: Location-based resource allocation algorithm
- **SMS Service**: Confirmation and alert notifications
- **Admin Dashboard**: Resource management interface
- **API Layer**: RESTful endpoints for integrations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Flask and dependencies (see `requirements.txt`)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd hackathon

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

The system will start on `http://localhost:12000`

### Testing the USSD Flow

```bash
# Run the demo script
python demo.py

# Or test manually
python test_ussd.py
```

## 📱 USSD Menu Structure

```
*123# - Emergency Response
├── 1 - Shelter
│   ├── Enter location
│   ├── View available options
│   └── Confirm selection
├── 2 - Food
│   ├── Enter location  
│   ├── View distribution centers
│   └── Confirm selection
└── 3 - Transport
    ├── Enter location
    ├── View transport options
    └── Confirm selection
```

## 🗄️ Database Schema

### Core Models:
- **User**: Phone number, name, location history
- **Resource**: Shelters, food centers, transport services
- **EmergencyRequest**: User requests and matching status
- **USSDSession**: Session state management

### Resource Types:
- `SHELTER`: Emergency accommodation facilities
- `FOOD`: Food distribution centers and kitchens
- `TRANSPORT`: Evacuation and medical transport

## 🌐 API Endpoints

### USSD Integration
- `POST /ussd/callback` - Telecom provider webhook
- `POST /ussd/test` - Testing endpoint

### Resource Management
- `GET /api/resources` - List all resources
- `POST /api/resources` - Add new resource
- `PUT /api/resources/{id}` - Update resource
- `GET /api/stats` - System statistics

### Admin Dashboard
- `GET /admin/` - Dashboard overview
- `GET /admin/resources` - Manage resources
- `GET /admin/requests` - View emergency requests

## 📊 Sample Data

The system comes pre-loaded with sample resources for Kogi State:

### Shelters:
- Lokoja Emergency Shelter (200 capacity)
- Confluence University Hostel (100 capacity)

### Food Centers:
- Red Cross Food Distribution Center (500 meals/day)
- Community Kitchen - Adankolo (200 meals/day)

### Transport:
- Emergency Evacuation Buses (50 passengers)
- Medical Emergency Transport (10 ambulances)

## 🔧 Configuration

### Environment Variables:
```bash
FLASK_ENV=development
DATABASE_URL=sqlite:///emergency_response.db
SMS_API_KEY=your_sms_api_key
SMS_GATEWAY_URL=https://api.sms-provider.com/send
```

### Telecom Integration:
The system is designed to work with major Nigerian telecom providers:
- MTN Nigeria
- Airtel Nigeria  
- Glo Mobile
- 9mobile

## 🚀 Deployment

### Production Setup:
1. **Server**: Deploy on cloud infrastructure (AWS, Azure, GCP)
2. **Database**: Use PostgreSQL for production
3. **USSD Gateway**: Partner with telecom aggregators
4. **SMS Service**: Integrate with Twilio, Nexmo, or local providers
5. **Monitoring**: Set up logging and alerting

### Scaling Considerations:
- Load balancing for high traffic
- Database replication for reliability
- CDN for static assets
- Auto-scaling based on demand

## 🤝 Integration Partners

### Government Agencies:
- National Emergency Management Agency (NEMA)
- State Emergency Management Agencies
- Local Government Areas

### NGOs and Organizations:
- Nigerian Red Cross Society
- UN Office for Coordination of Humanitarian Affairs
- International rescue organizations
- Local community groups

### Technology Partners:
- Telecom operators for USSD gateway
- SMS service providers
- Cloud infrastructure providers
- Mapping and location services

## 📈 Impact Metrics

### Key Performance Indicators:
- **Response Time**: Average time from request to resource match
- **Success Rate**: Percentage of requests successfully fulfilled
- **Coverage**: Number of locations and resources available
- **User Adoption**: Active users during emergency situations

### Expected Outcomes:
- 🕐 **50% faster** emergency response times
- 📱 **90% population reach** (basic phone penetration)
- 💰 **30% cost reduction** in coordination overhead
- 🎯 **Better resource utilization** through data-driven allocation

## 🔮 Future Enhancements

### Phase 2 Features:
- 🌍 **Multi-language support** (Hausa, Yoruba, Igbo)
- 🤖 **AI-powered resource prediction**
- 📍 **GPS integration** for precise location
- 🔄 **Real-time capacity updates**
- 📊 **Advanced analytics dashboard**

### Phase 3 Expansion:
- 🏥 **Medical emergency integration**
- 🚁 **Search and rescue coordination**
- 🌊 **Early warning system integration**
- 🌍 **Multi-country deployment**

## 🛡️ Security & Privacy

- **Data Encryption**: All communications encrypted in transit
- **Privacy Protection**: Minimal data collection, automatic cleanup
- **Access Control**: Role-based permissions for admin users
- **Audit Logging**: Complete audit trail of all actions

## 📞 Support & Contact

For technical support, partnership inquiries, or deployment assistance:

- **Email**: support@emergency-response.ng
- **Phone**: +234-XXX-XXX-XXXX
- **Documentation**: [docs.emergency-response.ng](https://docs.emergency-response.ng)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Nigerian Emergency Management Agency (NEMA)
- Telecom operators for USSD gateway support
- NGO partners for resource data
- Open source community for tools and libraries

---

**Built with ❤️ for disaster resilience in Nigeria and beyond**