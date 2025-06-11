#!/usr/bin/env python3
"""
Direct Use - Appointment Service
Simple, straightforward usage without test frameworks or dummy data.
"""
from helper.http.TAS_service import AppointmentService

def main():
    print("🚀 Appointment Service - Direct Use")
    print("=" * 50)
    
    # Get real container ID from user
    # cntr_id = input("Enter container ID: ").strip()
    cntr_id = "103936"
    if not cntr_id:
        print("❌ Container ID is required")
        return
    
    # Initialize service (will use environment variables if available, or defaults)
    service = AppointmentService()
    
    print(f"\n📝 Creating appointment for container: {cntr_id}")
    
    # Create appointment and send to server
    result = service.create_appointment(cntr_id)
    # result = service.update_appointment(cntr_id)

    # Show results
    print(f"\n📊 Results:")
    print(f"✅ Success: {result['success']}")
    print(f"📋 Status Code: {result.get('status_code', 'N/A')}")
    
    if result.get('response_file_path'):
        print(f"💾 Response saved to: {result['response_file_path']}")
    
    if result.get('appointment_status'):
        status = result['appointment_status']
        print(f"🔍 Return Code: {status.get('return_code', 'N/A')}")
        print(f"📦 Container ID: {status.get('container_id', 'N/A')}")
        
        if status.get('appointment_successful'):
            print("🎉 Appointment created successfully!")
        else:
            print("⚠️  Appointment failed")
            if status.get('fail_reason'):
                print(f"❌ Reason: {status.get('fail_reason')}")

if __name__ == "__main__":
    main() 