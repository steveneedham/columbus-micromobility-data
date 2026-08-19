#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Read event registry
const registryPath = path.join(__dirname, '../data-events-registry.json');
const templatePath = path.join(__dirname, '../micro-sites/events/template.html');

const registry = JSON.parse(fs.readFileSync(registryPath, 'utf8'));
const template = fs.readFileSync(templatePath, 'utf8');

// Process each event
registry.events.forEach(event => {
  // Format dates
  const eventStart = new Date(event.date_start);
  const eventEnd = new Date(event.date_end);
  const dateRange = `${eventStart.toLocaleDateString()} - ${eventEnd.toLocaleDateString()}`;

  const monStart = new Date(event.monitoring_start);
  const monEnd = new Date(event.monitoring_end);
  const monWindow = `${monStart.toLocaleDateString()} - ${monEnd.toLocaleDateString()}`;

  // Format attendance
  const attendance = new Intl.NumberFormat('en-US').format(event.expected_attendees);

  // Generate HTML
  let html = template
    .replace(/{{EVENT_NAME}}/g, event.name)
    .replace(/{{EVENT_SLUG}}/g, event.id)
    .replace(/{{EVENT_DATES}}/g, dateRange)
    .replace(/{{EVENT_LOCATION}}/g, event.location)
    .replace(/{{EVENT_ATTENDANCE}}/g, attendance)
    .replace(/{{MONITORING_WINDOW}}/g, monWindow)
    .replace(/{{EVENT_JSON}}/g, JSON.stringify(event));

  // Ensure directory exists
  const eventDir = path.join(__dirname, '../micro-sites/events', event.id);
  if (!fs.existsSync(eventDir)) {
    fs.mkdirSync(eventDir, { recursive: true });
  }

  // Write HTML file
  const outputPath = path.join(eventDir, 'index.html');
  fs.writeFileSync(outputPath, html);

  console.log(`✓ Generated: ${event.name} (${event.id})`);
});

console.log(`\n✅ Event microsites generated successfully`);
console.log(`Registry: ${registryPath}`);
