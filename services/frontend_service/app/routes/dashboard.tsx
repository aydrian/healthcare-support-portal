import { Link, useLoaderData } from 'react-router';
import { 
  Users, 
  MessageSquare, 
  FileText, 
  Activity,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { serverApi } from '@/lib/api.server';
import type { Patient, Document, User } from '@/lib/types';
import type { LoaderFunctionArgs } from 'react-router';

interface DashboardStats {
  totalPatients: number;
  totalDocuments: number;
  recentActivity: number;
  pendingTasks: number;
}

interface DashboardData {
  user: User;
  stats: DashboardStats;
  recentPatients: Patient[];
  recentDocuments: Document[];
}

// Loader function - fetch dashboard data
export async function loader({ request }: LoaderFunctionArgs) {
  try {
    // Require authentication
    const user = await requireAuth(request);
    
    // Get auth token from cookies
    const cookieHeader = request.headers.get('Cookie');
    const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
    
    if (!token) {
      throw new Response('Authentication required', { status: 401 });
    }
    
    // Load patients and documents in parallel
    const [patients, documents] = await Promise.all([
      serverApi.getPatients(token).catch(() => []),
      serverApi.getDocuments(token).catch(() => [])
    ]);

    // Calculate stats
    const stats: DashboardStats = {
      totalPatients: patients.length,
      totalDocuments: documents.length,
      recentActivity: patients.length + documents.length,
      pendingTasks: Math.floor(Math.random() * 5) + 1 // Mock pending tasks
    };

    // Get recent items (last 5)
    const recentPatients = patients.slice(-5).reverse();
    const recentDocuments = documents.slice(-5).reverse();

    return {
      user,
      stats,
      recentPatients,
      recentDocuments
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

function getUserDisplayName(user: User | null): string {
  if (!user) return 'Unknown User';
  return user.username || 'Unknown User';
}

export default function Dashboard() {
  const { user, stats, recentPatients, recentDocuments } = useLoaderData<DashboardData>();

  const getWelcomeMessage = () => {
    const hour = new Date().getHours();
    const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';
    return `${greeting}, ${getUserDisplayName(user)}`;
  };

  const quickActions = [
    {
      title: 'View Patients',
      description: 'Manage patient records and assignments',
      icon: Users,
      href: '/patients',
      color: 'bg-blue-500',
      show: ['doctor', 'nurse', 'admin'].includes(user?.role || '')
    },
    {
      title: 'Chat Assistant',
      description: 'Get AI-powered medical assistance',
      icon: MessageSquare,
      href: '/chat',
      color: 'bg-green-500',
      show: true
    },
    {
      title: 'Documents',
      description: 'Access medical documents and protocols',
      icon: FileText,
      href: '/documents',
      color: 'bg-purple-500',
      show: true
    }
  ].filter(action => action.show);


  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            {getWelcomeMessage()}
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Welcome back to the Healthcare Support Portal
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <Badge variant={user?.role as any} className="text-sm">
            {user?.role} • {user?.department}
          </Badge>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Users className="h-8 w-8 text-blue-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Total Patients
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.totalPatients}
                  </dd>
                </dl>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <FileText className="h-8 w-8 text-green-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Documents
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.totalDocuments}
                  </dd>
                </dl>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <TrendingUp className="h-8 w-8 text-purple-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Recent Activity
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.recentActivity}
                  </dd>
                </dl>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Clock className="h-8 w-8 text-orange-600" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Pending Tasks
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    {stats.pendingTasks}
                  </dd>
                </dl>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {quickActions.map((action) => (
            <Card key={action.title} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <Link to={action.href} className="block">
                  <div className="flex items-center">
                    <div className={`flex-shrink-0 w-10 h-10 rounded-lg ${action.color} flex items-center justify-center`}>
                      <action.icon className="h-6 w-6 text-white" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">
                        {action.title}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Recent Patients */}
        {recentPatients.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Recent Patients</CardTitle>
              <CardDescription>
                Latest patient records you have access to
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentPatients.map((patient) => (
                  <div key={patient.id} className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                        <Users className="h-4 w-4 text-gray-600" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {patient.name}
                      </p>
                      <p className="text-sm text-gray-500">
                        MRN: {patient.medical_record_number}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      <Badge variant={patient.is_active ? 'active' : 'inactive'}>
                        {patient.is_active ? 'Active' : 'Inactive'}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4">
                <Link to="/patients">
                  <Button variant="outline" size="sm" className="w-full">
                    View All Patients
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Recent Documents */}
        {recentDocuments.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Recent Documents</CardTitle>
              <CardDescription>
                Latest documents and protocols
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentDocuments.map((document) => (
                  <div key={document.id} className="flex items-center space-x-4">
                    <div className="flex-shrink-0">
                      <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center">
                        <FileText className="h-4 w-4 text-gray-600" />
                      </div>
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {document.title}
                      </p>
                      <p className="text-sm text-gray-500 capitalize">
                        {document.document_type} • {document.department}
                      </p>
                    </div>
                    <div className="flex-shrink-0">
                      {document.is_sensitive && (
                        <AlertCircle className="h-4 w-4 text-red-500" />
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4">
                <Link to="/documents">
                  <Button variant="outline" size="sm" className="w-full">
                    View All Documents
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
          <CardDescription>
            Current status of healthcare portal services
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-900">Auth Service</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-900">Patient Service</span>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-sm text-gray-900">RAG Service</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}