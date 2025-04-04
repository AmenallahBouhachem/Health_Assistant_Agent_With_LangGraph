// Existing imports and setup
const express = require('express');
const app = express();
const cors = require('cors');
const mongoose = require('mongoose');
const Chat = require('./models/Chat');
require('dotenv').config();
const port = process.env.PORT || 4000;


mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => console.log('Connected to MongoDB'))
.catch(err => {
  console.error('MongoDB connection error:', err);
  // Add more detailed error logging
  console.error('Connection string:', process.env.MONGO_URI);
});
app.use(express.json());
app.use(cors());

// Sample book names
const books = [
  { id: 1, name: 'gouga' },
  { id: 2, name: 'hachem' },
  { id: 3, name: 'Amen' },
];

const whatever = [
  { id: 1, name: 'wow' },
  { id: 2, name: 'omg' },
  { id: 3, name: 'jesus' },
];

// Predefined static texts for random response
const staticTexts = [
  "That's an interesting question!",
  "Let me think about that for a second.",
  "Here's something to consider!",
  "You always have great ideas, Gouga!",
  "Mazdar truly is an amazing city!",
];


app.get('/', (req, res) => {
    res.send('Backend is running!');
  });

// Endpoint to get book names
app.get('/api/books', (req, res) => {
  res.json(books);
});

app.get('/api/whatever', (req, res) => {
  res.json(whatever);
});

// Endpoint to handle prompts
app.post('/api/prompt', (req, res) => {
  const { prompt } = req.body;
  console.log("Received prompt:", prompt);

  // Randomly select one of the static texts
  const randomResponse = staticTexts[Math.floor(Math.random() * staticTexts.length)];
  
  // Respond to the frontend
  res.json({ reply: randomResponse });
});

app.post('/api/chats', async (req, res) => {
  try {
    const { name, bookId, whateverId } = req.body;

    const selectedBook = books.find(b => b.id === bookId);
    const selectedWhatever = whatever.find(w => w.id === whateverId);

    const newChat = new Chat({
      name,
      book: selectedBook ? selectedBook.name : null,
      whatever: selectedWhatever ? selectedWhatever.name : null,
      messages: []
    });

    const savedChat = await newChat.save();
    res.json(savedChat);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});


app.get('/api/chats', async (req, res) => {
  try {
    const chats = await Chat.find().sort({ createdAt: -1 });
    res.json(chats);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/chats/:chatId/messages', async (req, res) => {
  try {
    const chat = await Chat.findById(req.params.chatId);
    chat.messages.push({
      type: req.body.type,
      text: req.body.text
    });
    await chat.save();
    res.json(chat);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.get('/api/chats/:chatId', async (req, res) => {
  try {
    const chat = await Chat.findById(req.params.chatId);
    res.json(chat);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.put("/api/chats/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const { name } = req.body;  // You can update more fields if needed

    if (!name) return res.status(400).json({ error: "Name is required" });

    // Update only the 'name' field and return the updated chat
    const updatedChat = await Chat.findByIdAndUpdate(id, { name }, { new: true });

    if (!updatedChat) return res.status(404).json({ error: "Chat not found" });

    res.json(updatedChat);
  } catch (error) {
    res.status(500).json({ error: "Internal Server Error" });
  }
});

app.delete("/api/chats/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const deletedChat = await Chat.findByIdAndDelete(id);

    if (!deletedChat) return res.status(404).json({ error: "Chat not found" });

    res.json({ message: "Chat deleted successfully" });
  } catch (error) {
    res.status(500).json({ error: "Internal Server Error" });
  }
});



// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});