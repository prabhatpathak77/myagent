// State
let currentDate = new Date();
let selectedDate = null;
let meetings = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeCalendar();
    initializeTimeSlots();
    initializeModal();
    loadUpcomingMeetings();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // View toggle
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const view = e.target.dataset.view;
            handleViewChange(view);
        });
    });

    // Calendar navigation
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar();
    });

    // Category filters
    document.querySelectorAll('.category-item').forEach(item => {
        item.addEventListener('click', (e) => {
            const category = e.currentTarget.dataset.category;
            filterMeetingsByCategory(category);
        });
    });
}

// Calendar
function initializeCalendar() {
    renderCalendar();
}

function renderCalendar() {
    const grid = document.getElementById('calendarGrid');
    grid.innerHTML = '';

    // Update header
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'];
    document.getElementById('currentMonth').textContent = 
        `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;

    // Day headers
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayNames.forEach(day => {
        const header = document.createElement('div');
        header.className = 'calendar-day-header';
        header.textContent = day;
        grid.appendChild(header);
    });

    // Get first day of month and number of days
    const firstDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    const lastDay = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);
    const prevLastDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), 0);
    
    const firstDayIndex = firstDay.getDay();
    const lastDayDate = lastDay.getDate();
    const prevLastDayDate = prevLastDay.getDate();

    // Previous month days
    for (let i = firstDayIndex; i > 0; i--) {
        const day = createCalendarDay(prevLastDayDate - i + 1, true);
        grid.appendChild(day);
    }

    // Current month days
    const today = new Date();
    for (let i = 1; i <= lastDayDate; i++) {
        const isToday = i === today.getDate() && 
                       currentDate.getMonth() === today.getMonth() && 
                       currentDate.getFullYear() === today.getFullYear();
        const day = createCalendarDay(i, false, isToday);
        grid.appendChild(day);
    }

    // Next month days
    const remainingDays = 42 - (firstDayIndex + lastDayDate);
    for (let i = 1; i <= remainingDays; i++) {
        const day = createCalendarDay(i, true);
        grid.appendChild(day);
    }
}

function createCalendarDay(dayNum, isOtherMonth = false, isToday = false) {
    const day = document.createElement('div');
    day.className = 'calendar-day';
    if (isOtherMonth) day.classList.add('other-month');
    if (isToday) day.classList.add('today');
    
    // Check if day has meetings (mock data)
    if (Math.random() > 0.7) {
        day.classList.add('has-meeting');
    }
    
    day.textContent = dayNum;
    
    day.addEventListener('click', () => {
        selectedDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), dayNum);
        document.querySelectorAll('.calendar-day').forEach(d => d.classList.remove('selected'));
        day.classList.add('selected');
        updateTimeSlots(selectedDate);
    });
    
    return day;
}

// Time Slots
function initializeTimeSlots() {
    const container = document.getElementById('timeSlots');
    const times = generateTimeSlots();
    
    times.forEach(time => {
        const slot = document.createElement('div');
        slot.className = 'time-slot';
        slot.textContent = time;
        
        // Randomly mark some as unavailable (mock)
        if (Math.random() > 0.8) {
            slot.classList.add('unavailable');
        }
        
        slot.addEventListener('click', () => {
            if (!slot.classList.contains('unavailable')) {
                document.querySelectorAll('.time-slot').forEach(s => s.classList.remove('selected'));
                slot.classList.add('selected');
                
                // Pre-fill modal with selected time
                const [hours, minutes] = time.split(':');
                const period = time.includes('AM') || time.includes('PM') ? time.slice(-2) : '';
                let hour24 = parseInt(hours);
                if (period === 'PM' && hour24 !== 12) hour24 += 12;
                if (period === 'AM' && hour24 === 12) hour24 = 0;
                
                document.getElementById('meetingTime').value = 
                    `${hour24.toString().padStart(2, '0')}:${minutes.replace(/[^\d]/g, '').padStart(2, '0')}`;
            }
        });
        
        container.appendChild(slot);
    });
}

function generateTimeSlots() {
    const slots = [];
    for (let hour = 9; hour <= 17; hour++) {
        for (let min = 0; min < 60; min += 30) {
            const period = hour >= 12 ? 'PM' : 'AM';
            const displayHour = hour > 12 ? hour - 12 : hour;
            slots.push(`${displayHour}:${min.toString().padStart(2, '0')} ${period}`);
        }
    }
    return slots;
}

function updateTimeSlots(date) {
    // Refresh time slots based on selected date
    // In a real app, this would fetch availability from backend
    console.log('Selected date:', date);
}

// Modal
function initializeModal() {
    const modal = document.getElementById('modalOverlay');
    const createBtn = document.getElementById('createMeetingBtn');
    const closeBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const form = document.getElementById('meetingForm');

    createBtn.addEventListener('click', () => {
        modal.classList.add('active');
        // Set default date to today
        const today = new Date().toISOString().split('T')[0];
        document.getElementById('meetingDate').value = today;
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    cancelBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        handleCreateMeeting();
    });
}

function handleCreateMeeting() {
    const meeting = {
        title: document.getElementById('meetingTitle').value,
        date: document.getElementById('meetingDate').value,
        time: document.getElementById('meetingTime').value,
        duration: document.getElementById('meetingDuration').value,
        participants: document.getElementById('meetingParticipants').value,
        link: document.getElementById('meetingLink').value,
        category: document.getElementById('meetingCategory').value,
        notes: document.getElementById('meetingNotes').value
    };

    // In a real app, send to backend
    console.log('Creating meeting:', meeting);
    
    // Show success animation
    showNotification('Meeting created successfully!');
    
    // Close modal and reset form
    document.getElementById('modalOverlay').classList.remove('active');
    document.getElementById('meetingForm').reset();
    
    // Refresh meetings list
    loadUpcomingMeetings();
}

// Meetings
function loadUpcomingMeetings() {
    const container = document.getElementById('upcomingMeetings');
    
    // Mock data - in real app, fetch from backend
    const mockMeetings = [
        {
            time: 'Today, 2:00 PM',
            title: 'Product Review',
            participants: '5 participants',
            category: 'work'
        },
        {
            time: 'Tomorrow, 10:30 AM',
            title: 'Team Standup',
            participants: '8 participants',
            category: 'team'
        },
        {
            time: 'Nov 20, 3:00 PM',
            title: 'Client Meeting',
            participants: '3 participants',
            category: 'work'
        }
    ];

    container.innerHTML = mockMeetings.map(meeting => `
        <div class="meeting-card" style="border-left-color: ${getCategoryColor(meeting.category)}">
            <div class="meeting-time">${meeting.time}</div>
            <div class="meeting-title">${meeting.title}</div>
            <div class="meeting-participants">${meeting.participants}</div>
        </div>
    `).join('');
}

function getCategoryColor(category) {
    const colors = {
        work: '#667eea',
        personal: '#f093fb',
        team: '#4facfe'
    };
    return colors[category] || '#667eea';
}

function filterMeetingsByCategory(category) {
    console.log('Filtering by category:', category);
    // In real app, filter meetings display
}

// View handling
function handleViewChange(view) {
    if (view === 'week') {
        // Switch to week view
        console.log('Switching to week view');
        // In real app, render week view
    } else {
        // Switch to month view
        console.log('Switching to month view');
        renderCalendar();
    }
}

// Notifications
function showNotification(message) {
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 24px;
        right: 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
        z-index: 10000;
        animation: slideInRight 0.3s ease;
        font-weight: 500;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
