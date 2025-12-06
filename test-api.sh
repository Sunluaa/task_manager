#!/bin/bash

# Test Task Management System API

API_BASE="http://localhost:8000/api"
EMAIL="user@example.com"
PASSWORD="password123"

echo "🧪 Testing Task Management System API..."
echo ""

# Test 1: Login
echo "1️⃣  Testing Login..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

echo "Response: $LOGIN_RESPONSE"
TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ Login failed!"
  exit 1
fi

echo "✅ Login successful! Token: ${TOKEN:0:20}..."
echo ""

# Test 2: Get authenticated user
echo "2️⃣  Testing Get User (auth/me)..."
curl -s -X GET "$API_BASE/auth/me" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

# Test 3: Get all tasks
echo "3️⃣  Testing Get All Tasks..."
curl -s -X GET "$API_BASE/tasks/all" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

# Test 4: Create a task
echo "4️⃣  Testing Create Task..."
CREATE_RESPONSE=$(curl -s -X POST "$API_BASE/tasks/create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Test Task",
    "description":"This is a test task",
    "priority":"high",
    "status":"new"
  }')

echo "Response: $CREATE_RESPONSE"
TASK_ID=$(echo $CREATE_RESPONSE | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$TASK_ID" ]; then
  echo "❌ Task creation failed!"
  exit 1
fi

echo "✅ Task created! ID: $TASK_ID"
echo ""

# Test 5: Get task detail
echo "5️⃣  Testing Get Task Detail..."
curl -s -X GET "$API_BASE/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
echo ""

# Test 6: Update task
echo "6️⃣  Testing Update Task..."
curl -s -X PUT "$API_BASE/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Updated Test Task",
    "description":"Updated description",
    "priority":"urgent",
    "status":"in_progress"
  }' | jq '.'
echo ""

# Test 7: Delete task
echo "7️⃣  Testing Delete Task..."
curl -s -X DELETE "$API_BASE/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
echo ""
echo "✅ Task deleted!"
echo ""

echo "✅ All API tests completed successfully!"
