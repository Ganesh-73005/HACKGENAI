// MongoDB initialization script
const db = db.getSiblingDB("film_assist_db")

// Create collections
db.createCollection("users")
db.createCollection("stories")

// Create indexes
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ username: 1 }, { unique: true })
db.stories.createIndex({ user_id: 1 })
db.stories.createIndex({ created_at: -1 })
db.stories.createIndex({ title: "text", theme: "text" })

print("Database initialized successfully")
