import { useState } from 'react';
import { Link, Form, redirect, useNavigation } from 'react-router';
import { Activity, Eye, EyeOff } from 'lucide-react';
import { useForm, getFormProps, getInputProps, getSelectProps } from '@conform-to/react';
import { parseWithZod } from '@conform-to/zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { registerSchema } from '@/lib/schemas';
import { serverApi } from '@/lib/api.server';
import { handleFormSubmission, setAuthCookies } from '@/lib/utils/action-utils';
import { getCurrentUser, json } from '@/lib/utils/loader-utils';
import type { LoaderFunctionArgs, ActionFunctionArgs } from 'react-router';

const departments = [
  { value: 'cardiology', label: 'Cardiology' },
  { value: 'neurology', label: 'Neurology' },
  { value: 'pediatrics', label: 'Pediatrics' },
  { value: 'oncology', label: 'Oncology' },
  { value: 'emergency', label: 'Emergency Medicine' },
  { value: 'endocrinology', label: 'Endocrinology' },
  { value: 'general', label: 'General Medicine' },
];

const roles = [
  { value: 'doctor', label: 'Doctor' },
  { value: 'nurse', label: 'Nurse' },
  { value: 'admin', label: 'Administrator' },
];

// Loader function - check if already authenticated
export async function loader({ request }: LoaderFunctionArgs) {
  const user = await getCurrentUser(request);
  if (user) {
    // Already logged in, redirect to dashboard
    return redirect('/');
  }
  return null;
}

// Action function - handle registration form submission
export async function action({ request }: ActionFunctionArgs) {
  return handleFormSubmission(request, registerSchema, async (data) => {
    try {
      // Register the user
      const user = await serverApi.register(data);
      
      // Auto-login after registration
      const authResponse = await serverApi.login({
        username: data.username,
        password: data.password
      });
      const token = authResponse.access_token;
      
      // Create redirect response with auth cookies
      const response = redirect('/');
      return setAuthCookies(response, token, user);
    } catch (error: any) {
      // Return form error
      const submission = parseWithZod(await request.formData(), { schema: registerSchema });
      return json({
        submission: submission.reply({
          formErrors: [error.response?.data?.detail || 'Registration failed. Please try again.'],
        }),
      }, { status: 400 });
    }
  });
}

interface SignupProps {
  actionData?: {
    submission?: any;
  };
}

export default function Signup({ actionData }: SignupProps) {
  const [showPassword, setShowPassword] = useState(false);
  const navigation = useNavigation();
  const isSubmitting = navigation.state === 'submitting';
  
  const [form, fields] = useForm({
    lastResult: actionData?.submission,
    onValidate({ formData }) {
      return parseWithZod(formData, { schema: registerSchema });
    },
    shouldValidate: 'onBlur',
    shouldRevalidate: 'onInput',
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Logo and Title */}
        <div className="text-center">
          <div className="mx-auto h-16 w-16 bg-healthcare-blue rounded-2xl flex items-center justify-center">
            <Activity className="h-10 w-10 text-white" />
          </div>
          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900">
            Join Healthcare Portal
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Create your account to get started
          </p>
        </div>

        {/* Registration Form */}
        <Card>
          <CardHeader>
            <CardTitle>Create Account</CardTitle>
            <CardDescription>
              Fill in your information to create a new account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Form method="post" {...getFormProps(form)} className="space-y-6">
              {form.errors && (
                <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
                  {form.errors.join(', ')}
                </div>
              )}

              <div>
                <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1">
                  Username
                </label>
                <Input
                  {...getInputProps(fields.username, { type: 'text' })}
                  placeholder="Choose a username"
                  className="w-full"
                />
                {fields.username.errors && (
                  <p className="mt-1 text-sm text-red-600">
                    {fields.username.errors.join(', ')}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                <Input
                  {...getInputProps(fields.email, { type: 'email' })}
                  placeholder="Enter your email address"
                  className="w-full"
                />
                {fields.email.errors && (
                  <p className="mt-1 text-sm text-red-600">
                    {fields.email.errors.join(', ')}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <div className="relative">
                  <Input
                    {...getInputProps(fields.password, { type: showPassword ? 'text' : 'password' })}
                    placeholder="Create a password"
                    className="w-full pr-10"
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4 text-gray-400" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400" />
                    )}
                  </button>
                </div>
                {fields.password.errors && (
                  <p className="mt-1 text-sm text-red-600">
                    {fields.password.errors.join(', ')}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <select
                  {...getSelectProps(fields.role)}
                  className="w-full h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  {roles.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
                {fields.role.errors && (
                  <p className="mt-1 text-sm text-red-600">
                    {fields.role.errors.join(', ')}
                  </p>
                )}
              </div>

              <div>
                <label htmlFor="department" className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <select
                  {...getSelectProps(fields.department)}
                  className="w-full h-10 px-3 py-2 border border-input bg-background rounded-md text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                >
                  {departments.map((dept) => (
                    <option key={dept.value} value={dept.value}>
                      {dept.label}
                    </option>
                  ))}
                </select>
                {fields.department.errors && (
                  <p className="mt-1 text-sm text-red-600">
                    {fields.department.errors.join(', ')}
                  </p>
                )}
              </div>

              <Button
                type="submit"
                disabled={isSubmitting}
                className="w-full"
                variant="healthcare"
              >
                {isSubmitting ? (
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Creating account...
                  </div>
                ) : (
                  'Create Account'
                )}
              </Button>
            </Form>

            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">
                    Already have an account?
                  </span>
                </div>
              </div>

              <div className="mt-6">
                <Link to="/login">
                  <Button variant="outline" className="w-full">
                    Sign in instead
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}