import { MongoClient } from 'mongodb';

let client;

export async function db() {
  if (!client) {
    client = new MongoClient(process.env.MONGO_URI, {
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 1500,
      connectTimeoutMS: 1500,
      socketTimeoutMS: 5000
    });
    await client.connect();
  }
  return client.db(process.env.DB_NAME || 'efofx');
}

export async function closeConnection() {
  if (client) {
    await client.close();
    client = null;
  }
}
