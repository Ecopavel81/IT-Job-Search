import React, { useState, useEffect } from 'react';
import { Search, MapPin, Briefcase, Send, Paperclip, MessageSquare, Bell, RefreshCw, CheckCircle, Clock, XCircle } from 'lucide-react';

const JobSearchSystem = () => {
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedLocation, setSelectedLocation] = useState('all');
  const [selectedPosition, setSelectedPosition] = useState('all');
  const [selectedJob, setSelectedJob] = useState(null);
  const [applications, setApplications] = useState([]);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [notification, setNotification] = useState(null);
  const [applicationForm, setApplicationForm] = useState({
    name: '',
    email: '',
    phone: '',
    message: '',
    resume: null
  });
  const [showSearchSuggestions, setShowSearchSuggestions] = useState(false);

  const priorityLocations = ['Dubai', 'Canada', 'Ireland', 'Serbia'];
  const positions = ['ML Engineer', 'AI Developer', 'Data Scientist'];

  // Словарь синонимов и связанных терминов для улучшенного поиска
  const searchDictionary = {
    'ml': ['machine learning', 'машинное обучение', 'ml', 'машинное обучение'],
    'machine learning': ['ml', 'машинное обучение', 'artificial intelligence', 'ai'],
    'ai': ['artificial intelligence', 'искусственный интеллект', 'ai', 'машинное обучение', 'ml'],
    'artificial intelligence': ['ai', 'искусственный интеллект', 'machine learning', 'ml'],
    'data science': ['data scientist', 'анализ данных', 'data analysis', 'статистика'],
    'data scientist': ['data science', 'анализ данных', 'data analyst', 'статистик'],
    'python': ['питон', 'python3', 'py', 'программирование'],
    'tensorflow': ['tf', 'tensor flow', 'глубокое обучение'],
    'pytorch': ['torch', 'глубокое обучение', 'neural networks'],
    'deep learning': ['глубокое обучение', 'нейронные сети', 'neural networks', 'dl'],
    'nlp': ['natural language processing', 'обработка естественного языка', 'текст'],
    'computer vision': ['cv', 'компьютерное зрение', 'image processing', 'обработка изображений'],
    'mlops': ['ml ops', 'machine learning operations', 'devops', 'deployment'],
    'engineer': ['инженер', 'разработчик', 'developer', 'программист'],
    'developer': ['разработчик', 'программист', 'engineer', 'инженер'],
    'scientist': ['ученый', 'исследователь', 'researcher', 'аналитик'],
    'analyst': ['аналитик', 'исследователь', 'analyst', 'scientist']
  };

  // Моковые данные для демонстрации
  const mockJobs = [
    {
      id: 1,
      title: 'Senior ML Engineer',
      company: 'TechCorp Dubai',
      location: 'Dubai',
      position: 'ML Engineer',
      salary: '$120k-180k',
      description: 'Looking for experienced ML Engineer with strong Python and TensorFlow skills.',
      requirements: ['Python', 'TensorFlow', 'Deep Learning', 'MLOps'],
      postedDate: '2025-10-20'
    },
    {
      id: 2,
      title: 'AI Research Scientist',
      company: 'AI Labs Canada',
      location: 'Canada',
      position: 'AI Developer',
      salary: '$150k-200k',
      description: 'Join our research team working on cutting-edge NLP projects.',
      requirements: ['Python', 'PyTorch', 'NLP', 'Research Experience'],
      postedDate: '2025-10-22'
    },
    {
      id: 3,
      title: 'Data Scientist',
      company: 'DataCo Ireland',
      location: 'Ireland',
      position: 'Data Scientist',
      salary: '€80k-120k',
      description: 'Seeking Data Scientist for analytics and ML model development.',
      requirements: ['Python', 'SQL', 'Machine Learning', 'Statistics'],
      postedDate: '2025-10-24'
    }
  ];

  // Инициализация данных
  useEffect(() => {
    setJobs(mockJobs);
    setFilteredJobs(mockJobs);
  }, []);

  // Расширенная функция поиска с учетом синонимов
  const expandSearchTerms = (term) => {
    const lowerTerm = term.toLowerCase().trim();
    const relatedTerms = [lowerTerm];

    // Добавляем синонимы из словаря
    if (searchDictionary[lowerTerm]) {
      relatedTerms.push(...searchDictionary[lowerTerm]);
    }

    return relatedTerms;
  };

  // Фильтрация вакансий
  useEffect(() => {
    let result = jobs;

    // Фильтр по поисковому запросу с учетом синонимов
    if (searchTerm.trim()) {
      const searchTerms = expandSearchTerms(searchTerm);
      result = result.filter(job => {
        const searchableText = `${job.title} ${job.company} ${job.description} ${job.requirements.join(' ')}`.toLowerCase();
        return searchTerms.some(term => searchableText.includes(term));
      });
    }

    // Фильтр по локации
    if (selectedLocation !== 'all') {
      result = result.filter(job => job.location === selectedLocation);
    }

    // Фильтр по позиции
    if (selectedPosition !== 'all') {
      result = result.filter(job => job.position === selectedPosition);
    }

    setFilteredJobs(result);
  }, [searchTerm, selectedLocation, selectedPosition, jobs]);

  // Обработка отправки заявки
  const handleApplicationSubmit = (e) => {
    e.preventDefault();

    const newApplication = {
      id: Date.now(),
      jobId: selectedJob.id,
      jobTitle: selectedJob.title,
      ...applicationForm,
      status: 'pending',
      appliedDate: new Date().toISOString()
    };

    setApplications([...applications, newApplication]);
    setShowApplicationModal(false);
    setApplicationForm({ name: '', email: '', phone: '', message: '', resume: null });

    // Показать уведомление
    showNotification('Application submitted successfully!', 'success');
  };

  // Показать уведомление
  const showNotification = (message, type) => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 3000);
  };

  // Обработка загрузки файла
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setApplicationForm({ ...applicationForm, resume: file });
    }
  };

  // Получить статус иконку
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending': return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'accepted': return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'rejected': return <XCircle className="w-5 h-5 text-red-500" />;
      default: return <Clock className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Уведомления */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
        } text-white flex items-center gap-2`}>
          <Bell className="w-5 h-5" />
          {notification.message}
        </div>
      )}

      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8 text-gray-800">IT Job Search System</h1>

        {/* Панель фильтров */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Поиск */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search jobs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onFocus={() => setShowSearchSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSearchSuggestions(false), 200)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Фильтр по локации */}
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">All Locations</option>
                {priorityLocations.map(loc => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
            </div>

            {/* Фильтр по позиции */}
            <div className="relative">
              <Briefcase className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <select
                value={selectedPosition}
                onChange={(e) => setSelectedPosition(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none"
              >
                <option value="all">All Positions</option>
                {positions.map(pos => (
                  <option key={pos} value={pos}>{pos}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Список вакансий */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {filteredJobs.length > 0 ? (
            filteredJobs.map(job => (
              <div key={job.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-800">{job.title}</h3>
                    <p className="text-gray-600">{job.company}</p>
                  </div>
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                    {job.salary}
                  </span>
                </div>

                <div className="flex gap-4 mb-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {job.location}
                  </div>
                  <div className="flex items-center gap-1">
                    <Briefcase className="w-4 h-4" />
                    {job.position}
                  </div>
                </div>

                <p className="text-gray-700 mb-4">{job.description}</p>

                <div className="flex flex-wrap gap-2 mb-4">
                  {job.requirements.map((req, idx) => (
                    <span key={idx} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                      {req}
                    </span>
                  ))}
                </div>

                <button
                  onClick={() => {
                    setSelectedJob(job);
                    setShowApplicationModal(true);
                  }}
                  className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Apply Now
                </button>
              </div>
            ))
          ) : (
            <div className="col-span-2 text-center py-12 text-gray-500">
              <RefreshCw className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No jobs found matching your criteria</p>
            </div>
          )}
        </div>

        {/* История заявок */}
        {applications.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
              <MessageSquare className="w-6 h-6" />
              My Applications
            </h2>
            <div className="space-y-4">
              {applications.map(app => (
                <div key={app.id} className="border border-gray-200 rounded-lg p-4 flex justify-between items-center">
                  <div>
                    <h4 className="font-semibold text-gray-800">{app.jobTitle}</h4>
                    <p className="text-sm text-gray-600">Applied on {new Date(app.appliedDate).toLocaleDateString()}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(app.status)}
                    <span className="text-sm capitalize">{app.status}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Модальное окно подачи заявки */}
      {showApplicationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <div>
                  <h2 className="text-2xl font-semibold text-gray-800">Apply for Position</h2>
                  <p className="text-gray-600">{selectedJob?.title} at {selectedJob?.company}</p>
                </div>
                <button
                  onClick={() => setShowApplicationModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XCircle className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleApplicationSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name *</label>
                  <input
                    type="text"
                    required
                    value={applicationForm.name}
                    onChange={(e) => setApplicationForm({ ...applicationForm, name: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email *</label>
                  <input
                    type="email"
                    required
                    value={applicationForm.email}
                    onChange={(e) => setApplicationForm({ ...applicationForm, email: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                  <input
                    type="tel"
                    value={applicationForm.phone}
                    onChange={(e) => setApplicationForm({ ...applicationForm, phone: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Cover Letter</label>
                  <textarea
                    value={applicationForm.message}
                    onChange={(e) => setApplicationForm({ ...applicationForm, message: e.target.value })}
                    rows="4"
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Tell us why you're a great fit..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Resume *</label>
                  <div className="flex items-center gap-2">
                    <label className="flex-1 cursor-pointer">
                      <div className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2">
                        <Paperclip className="w-5 h-5 text-gray-400" />
                        <span className="text-gray-600">
                          {applicationForm.resume ? applicationForm.resume.name : 'Choose file...'}
                        </span>
                      </div>
                      <input
                        type="file"
                        required
                        onChange={handleFileChange}
                        accept=".pdf,.doc,.docx"
                        className="hidden"
                      />
                    </label>
                  </div>
                </div>

                <div className="flex gap-4 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowApplicationModal(false)}
                    className="flex-1 px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
                  >
                    <Send className="w-4 h-4" />
                    Submit Application
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobSearchSystem;
