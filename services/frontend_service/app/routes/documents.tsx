import { useState, useEffect } from 'react';
import { 
  Plus, 
  Search, 
  Filter, 
  FileText, 
  Upload, 
  Eye, 
  Download,
  AlertCircle,
  Calendar,
  User as UserIcon
} from 'lucide-react';
import { useLoaderData, Form } from 'react-router';
import { useForm, getFormProps, getInputProps, getSelectProps } from '@conform-to/react';
import { parseWithZod } from '@conform-to/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDateTime, truncateText } from '@/lib/utils';
import { requireAuth, handleApiError } from '@/lib/utils/loader-utils';
import { handleFormSubmission } from '@/lib/utils/action-utils';
import { serverApi } from '@/lib/api.server';
import { documentCreateSchema } from '@/lib/schemas';
import type { Document, User } from '@/lib/types';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

interface DocumentsData {
  user: User;
  documents: Document[];
}

// Loader function - fetch documents data
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
    
    // Load documents
    const documents = await serverApi.getDocuments(token);

    return {
      user,
      documents
    };
  } catch (error) {
    throw handleApiError(error);
  }
}

// Action function - handle document creation
export async function action({ request }: ActionFunctionArgs) {
  const user = await requireAuth(request);
  const cookieHeader = request.headers.get('Cookie');
  const token = cookieHeader?.match(/authToken=([^;]+)/)?.[1];
  
  if (!token) {
    throw new Response('Authentication required', { status: 401 });
  }

  return handleFormSubmission(request, documentCreateSchema, async (data) => {
    // Add user context to document data
    const documentData = {
      ...data,
      department: data.department || user.department, // Use user's department as default
    };
    
    await serverApi.createDocument(documentData, token);
    // No need to return anything - handleFormSubmission will handle success
  });
}

export default function Documents() {
  const { user, documents } = useLoaderData<DocumentsData>();
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>(documents);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [departmentFilter, setDepartmentFilter] = useState('all');

  useEffect(() => {
    filterDocuments();
  }, [documents, searchTerm, typeFilter, departmentFilter]);

  const filterDocuments = () => {
    let filtered = documents;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(doc =>
        doc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        doc.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(doc => doc.document_type === typeFilter);
    }

    // Department filter
    if (departmentFilter !== 'all') {
      filtered = filtered.filter(doc => doc.department === departmentFilter);
    }

    setFilteredDocuments(filtered);
  };

  const documentTypes = Array.from(new Set(documents.map(d => d.document_type))).sort();
  const departments = Array.from(new Set(documents.map(d => d.department))).sort();

  const getDocumentIcon = (type: string) => {
    switch (type) {
      case 'protocol':
        return '📋';
      case 'policy':
        return '📜';
      case 'guideline':
        return '📖';
      case 'research':
        return '🔬';
      case 'report':
        return '📊';
      case 'medical_record':
        return '📝';
      default:
        return '📄';
    }
  };


  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Documents
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Access medical documents, protocols, and policies
          </p>
        </div>
        <div className="mt-4 flex space-x-2 md:ml-4 md:mt-0">
          <Button variant="outline">
            <Upload className="mr-2 h-4 w-4" />
            Upload
          </Button>
          <Button variant="healthcare">
            <Plus className="mr-2 h-4 w-4" />
            New Document
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <Input
                placeholder="Search documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="all">All Types</option>
              {documentTypes.map(type => (
                <option key={type} value={type} className="capitalize">
                  {type.replace('_', ' ')}
                </option>
              ))}
            </select>
            <select
              value={departmentFilter}
              onChange={(e) => setDepartmentFilter(e.target.value)}
              className="h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <option value="all">All Departments</option>
              {departments.map(dept => (
                <option key={dept} value={dept} className="capitalize">
                  {dept}
                </option>
              ))}
            </select>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <FileText className="h-4 w-4" />
              <span>{filteredDocuments.length} documents</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Documents Grid */}
      {filteredDocuments.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No documents found</h3>
            <p className="mt-1 text-sm text-gray-500">
              {documents.length === 0 
                ? "Get started by uploading your first document."
                : "Try adjusting your search or filter criteria."
              }
            </p>
            {documents.length === 0 && (
              <div className="mt-6">
                <Button variant="healthcare">
                  <Plus className="mr-2 h-4 w-4" />
                  Add Document
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          {filteredDocuments.map((document) => (
            <Card key={document.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">
                      {getDocumentIcon(document.document_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <CardTitle className="text-lg leading-6">
                        {document.title}
                      </CardTitle>
                      <div className="flex items-center space-x-2 mt-1">
                        <Badge 
                          variant="outline"
                          className="text-xs capitalize"
                        >
                          {document.document_type.replace('_', ' ')}
                        </Badge>
                        {document.is_sensitive && (
                          <Badge variant="destructive" className="text-xs">
                            <AlertCircle className="mr-1 h-3 w-3" />
                            Sensitive
                          </Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <p className="text-sm text-gray-600 line-clamp-3">
                    {truncateText(document.content, 120)}
                  </p>
                  
                  <div className="space-y-1 text-xs text-gray-500">
                    <div className="flex items-center">
                      <Filter className="mr-2 h-3 w-3" />
                      <span className="capitalize">Department: {document.department}</span>
                    </div>
                    <div className="flex items-center">
                      <Calendar className="mr-2 h-3 w-3" />
                      <span>Created: {formatDateTime(document.created_at)}</span>
                    </div>
                    {document.created_by && (
                      <div className="flex items-center">
                        <UserIcon className="mr-2 h-3 w-3" />
                        <span>By: {document.created_by.username}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex space-x-2 pt-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Eye className="mr-1 h-3 w-3" />
                      View
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Download className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {documents.length}
              </div>
              <div className="text-sm text-gray-500">Total Documents</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {documents.filter(d => d.department === user?.department).length}
              </div>
              <div className="text-sm text-gray-500">My Department</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {documents.filter(d => d.is_sensitive).length}
              </div>
              <div className="text-sm text-gray-500">Sensitive</div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {documentTypes.length}
              </div>
              <div className="text-sm text-gray-500">Document Types</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Upload Zone */}
      <Card className="border-2 border-dashed border-gray-300 hover:border-gray-400 transition-colors">
        <CardContent className="p-8">
          <div className="text-center">
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              Upload new documents
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Drag and drop files here, or click to browse
            </p>
            <div className="mt-6">
              <Button variant="outline">
                <Upload className="mr-2 h-4 w-4" />
                Choose Files
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}