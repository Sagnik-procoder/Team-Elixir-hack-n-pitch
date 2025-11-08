const mongoose = require('mongoose');

mongoose.connect("mongodb+srv://demouse:rupam2629@cluster0.ylqzjet.mongodb.net/mental_health?retryWrites=true&w=majority&appName=Cluster0")
const doctorSchema = new mongoose.Schema({
    fullName: {
        type: String,
        required: true,
        trim: true 
    },
    email: {
        type: String,
        required: true,
        unique: true,  
        lowercase: true, 
        trim: true
    },
    specialization: {
        type: String,
        required: true,
        enum: [
            'cardiology', 
            'dermatology', 
            'general_physician', 
            'gynecology', 
            'neurology', 
            'orthopedics', 
            'pediatrics', 
            'psychiatry', 
            'other'
        ]
    },



    location: {
        type: String,
        required: true,
      
        enum: [
            'Garhbeta',
            'Mednipur',
            'Bankur',
            'Chandrokona',
            'Godapiasole',
            'Kolkata',
            'Arambag',
            'ahmedabad' 
        ]
    },


    experience: {
        type: Number,
        required: true,
        min: 0 
    },
    fees: {
        type: Number,
        required: true,
        min: 0 
    },
    link:String,
    availableTime: {
        type: String,
        required: true,
        trim: true,
        default: 'Not Specified' 
    }
}, {
   
    timestamps: true 
});

const Doctor = mongoose.model('Doctor', doctorSchema);

module.exports = Doctor;
