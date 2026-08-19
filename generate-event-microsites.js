#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Read the template
const templatePath = path.join(__dirname, 'micro-sites/events/template.html');
const template = fs.readFileSync(templatePath, 'utf8');

// Read the event registry
const registryPath = path.join(__dirname, 'data-events-registry.json');
const registry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));

// Ensure events output directory exists
const eventsDir = path.join(__dirname, 'micro-sites/events');
if (!fs.existsSync(eventsDir)) {
  fs.mkdirSync(eventsDir, { recursive: true });
}

// Generate a microsite for each event
registry.events.forEach(event => {
  const eventSlug = event.id;
  const eventDir = path.join(eventsDir, eventSlug);

  // Create event directory if it doesn't exist
  if (!fs.existsSync(eventDir)) {
    fs.mkdirSync(eventDir, { recursive: true });
  }

  // Format the monitoring window display
  const monitoringStart = new Date(event.monitoring_start);
  const monitoringEnd = new Date(event.monitoring_end);
  const monitoringWindow = `${monitoringStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${monitoringEnd.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;

  // Format event date for display
  const eventDate = new Date(event.date);
  const formattedDate = eventDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' });

  // Format expected attendance with commas
  const formattedAttendance = event.expected_attendance.toLocaleString();

  // Create event JSON for embedding in the template
  const eventJson = JSON.stringify({
    geofence: event.geofence
  });

  // Replace all placeholders in the template
  let html = template
    .replace(/{{EVENT_NAME}}/g, event.name)
    .replace(/{{EVENT_SLUG}}/g, eventSlug)
    .replace(/{{EVENT_DATE}}/g, formattedDate)
    .replace(/{{EVENT_CATEGORY}}/g, event.category)
    .replace(/{{EVENT_VENUE}}/g, event.venue)
    .replace(/{{EVENT_ATTENDANCE}}/g, formattedAttendance)
    .replace(/{{MONITORING_WINDOW}}/g, monitoringWindow)
    .replace(/{{HERO_IMAGE}}/g, event.hero_image)
    .replace(/{{EVENT_JSON}}/g, eventJson);

  // Write the generated HTML to the event directory
  const outputPath = path.join(eventDir, 'index.html');
  fs.writeFileSync(outputPath, html, 'utf8');

  console.log(`Generated: ${eventSlug}/index.html`);
});

console.log(`\nSuccessfully generated ${registry.events.length} event microsites.`);
