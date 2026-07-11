import { createClient } from '@supabase/supabase-js';
const url = "https://ntxhesitmpzhvllpxoxq.supabase.co";
const key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50eGhlc2l0bXB6aHZsbHB4b3hxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM3MDM2NzcsImV4cCI6MjA5OTI3OTY3N30.LzPJ3_PSaZbeOVtB8JnGiL-TgWEbuftzHZTMf8oJ6Tw";
const supabase = createClient(url, key);

async function test() {
    const { data, error } = await supabase.from('chats').select('id').limit(1);
    console.log("chats:", data, error);
}
test();
