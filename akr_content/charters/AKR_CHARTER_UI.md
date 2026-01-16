# AKR Charter: UI Component Documentation

**Version**: 1.0  
**Last Updated**: 2025-11-02  
**Extends**: AKR_CHARTER.md (universal principles)  
**Applies To**: UI components, React components, frontend pages, hooks, utilities

---

## Purpose

This charter extends the universal **AKR_CHARTER.md** with conventions specific to UI component documentation. It applies to frontend components, pages, custom hooks, and UI utilities across modern web frameworks (React, Vue, Angular, etc.).

**Prerequisites**: Read AKR_CHARTER.md first for:
- Core principles (Lean, Flexible, Evolutionary, etc.)
- Universal conventions (feature tags, Git format)
- Documentation tiers (Essential/Recommended/Optional)

**This charter adds**:
- Component naming and organizational patterns
- UI component documentation structure
- Props/state documentation conventions
- Enterprise best practices for maintainable UI documentation
- Accessibility and UX documentation patterns

---

## UI Component Context

### What We Document

**Target:** Reusable UI components, pages, custom hooks, and UI utilities

```
Frontend Architecture:

┌──────────────────────┐
│   Pages/Views        │  → Document when: Complex business logic, multi-component orchestration
│   (Route Components) │     Example: Dashboard.tsx, AdminPanel.tsx
└──────────────────────┘
           ↓
┌──────────────────────┐
│   ► COMPONENTS ◄     │  ← THIS is what we document most
│   (Reusable UI)      │     Example: Button, Card, Table, Modal
│   - Presentation     │
│   - Business Logic   │
│   - Composition      │
└──────────────────────┘
           ↓
┌──────────────────────┐
│   Custom Hooks       │  → Document when: Complex state logic, reusable behavior
│   (Behavior)         │     Example: useAuth, useForm, usePagination
└──────────────────────┘
           ↓
┌──────────────────────┐
│   Services/Utils     │  → Use Backend Charter for API services
│   (Business Logic)   │     Use this charter for UI utilities
└──────────────────────┘
```

**Why focus on components?**
- Components are the building blocks of UI (reused across app)
- Props/state contracts define component API
- Accessibility requirements critical for compliance
- Visual behavior not always obvious from code
- UX patterns and interaction flows need documentation

**What we do NOT document here:**
- API services → Use AKR_CHARTER_BACKEND.md
- Database schemas → Use AKR_CHARTER_DB.md
- Simple utility functions → Code comments sufficient
- Auto-generated TypeScript types → Self-documenting

---

## Component Naming Conventions

### Component Files

**Format**: `PascalCase.tsx` (React/TypeScript) or `PascalCase.jsx` (React/JavaScript)

**Examples**:
- ✅ `Button.tsx` (simple component)
- ✅ `CourseCard.tsx` (domain-specific component)
- ✅ `AdminPanel.tsx` (page/view component)
- ✅ `useAuth.ts` (custom hook)
- ✅ `dateFormatter.ts` (utility)
- ❌ `button.tsx` (use PascalCase)
- ❌ `course-card.tsx` (use PascalCase, not kebab-case)
- ❌ `admin_panel.tsx` (use PascalCase, not snake_case)

**Co-located files**:
```
Button/
├── Button.tsx              ← Component implementation
├── Button.module.css       ← Component styles (CSS Modules)
├── Button.test.tsx         ← Component tests
├── Button.stories.tsx      ← Storybook stories (if using)
├── Button_doc.md           ← Component documentation
└── index.ts                ← Barrel export (optional)
```

**Alternative flat structure**:
```
components/common/
├── Button.tsx
├── Button.module.css
├── Button.test.tsx
├── Button_doc.md
├── Card.tsx
├── Card.module.css
└── Card_doc.md
```

---

### Component Naming Patterns

**Presentational components** (UI only, no business logic):
```
✅ Button, Card, Badge, Avatar, Icon
✅ Table, List, Grid, Layout
✅ Modal, Dialog, Drawer, Popover
✅ Input, Select, Checkbox, TextArea
```

**Container components** (business logic + data fetching):
```
✅ CourseList, EnrollmentTable, UserProfile
✅ DashboardSummary, AdminPanel, CourseCatalog
```

**Page components** (route-level):
```
✅ Dashboard, CourseCatalog, AdminPanel, NotFound
✅ UserProfile, CourseDetails, EnrollmentHistory
```

**Composite components** (composition of smaller components):
```
✅ CourseCard (contains Badge, Button, Image)
✅ EnrollmentRow (contains StatusBadge, Actions)
✅ AdminTable (contains Table, Pagination, Search)
```

**Higher-Order Components (HOCs)**:
```
✅ withAuth(Component)
✅ withLoading(Component)
✅ withErrorBoundary(Component)
```

**Custom hooks** (reusable logic):
```
✅ useAuth, useForm, usePagination
✅ useCourses, useEnrollments, useUsers
✅ useDebounce, useLocalStorage, useMediaQuery
```

---

### Props and State Naming

**Props interface naming**:
```typescript
// ✅ Component name + Props suffix
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
  children: React.ReactNode;
}

// ✅ For generic components
export interface TableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  onRowClick?: (row: T) => void;
}
```

**Boolean props**:
```typescript
✅ isLoading, isDisabled, isOpen, isActive
✅ hasError, hasData, hasPermission
✅ canEdit, canDelete, canCreate
✅ showHeader, showFooter, showBorder

❌ loading (ambiguous - is it a boolean or object?)
❌ error (is it boolean or error object?)
❌ open (is it boolean or function?)
```

**Event handler props**:
```typescript
✅ onClick, onChange, onSubmit, onClose
✅ onEnrollmentCreate, onCourseUpdate, onUserDelete
✅ onSuccess, onError, onComplete

❌ click, change, submit (missing "on" prefix)
❌ handleClick (implementation detail, not API)
```

**Render prop naming**:
```typescript
✅ renderHeader, renderFooter, renderRow
✅ renderEmpty, renderError, renderLoading

// Usage
<Table
  data={courses}
  renderRow={(course) => <CourseRow course={course} />}
  renderEmpty={() => <EmptyState message="No courses" />}
/>
```

---

## Component Documentation Structure

### Essential Sections (Tier 1 - Always Required)

**Minimum viable documentation** (10-15 minutes):

```markdown
✅ Component Identification
   - Name, file location, type (presentational/container)
   
✅ Purpose & Usage
   - What this component does (1-2 sentences)
   - When to use it
   - When NOT to use it (alternatives)

✅ Props API
   - All props with types and descriptions
   - Required vs optional
   - Default values

✅ Visual Examples
   - At least 1 example (code + screenshot/description)
   - Common use cases
```

**Time**: 10-15 minutes (AI can generate 50%, human adds 50%)

---

### Recommended Sections (Tier 2 - Include When Applicable)

Add these when the information exists and is valuable:

```markdown
✅ States and Variants
   - Visual states (default, hover, active, disabled, loading, error)
   - Variants (primary, secondary, danger, etc.)

✅ Accessibility
   - ARIA attributes used
   - Keyboard navigation support
   - Screen reader behavior

✅ Styling and Theming
   - CSS classes applied
   - Theming variables/props
   - Customization options

✅ Component Behavior
   - User interactions (click, hover, drag, etc.)
   - State management (controlled vs uncontrolled)
   - Side effects (API calls, local storage, etc.)
```

**Time**: +10-15 minutes to baseline documentation

---

### Optional Sections (Tier 3 - Add When Needed)

**Event-driven documentation** - add sections when circumstances warrant:

```markdown
⏳ Related Components
   Add when: Component is part of composition pattern

⏳ Performance Considerations
   Add when: Component is performance-sensitive, virtualization, memoization

⏳ Known Issues & Limitations
   Add when: Browser compatibility issues, known bugs, workarounds

⏳ Migration Guide
   Add when: Breaking changes from previous version

⏳ Testing Guidance
   Add when: Complex testing scenarios, mocking requirements

⏳ Advanced Usage
   Add when: Complex patterns, render props, compound components

⏳ Browser Compatibility
   Add when: Component uses modern APIs with limited support

⏳ Design Tokens
   Add when: Design system integration, token mapping
```

**Time**: 10-15 minutes per optional section (add incrementally)

---

## Component Documentation Patterns

### Props API Documentation

**Format**: Table with type, required, default, description

```markdown
## Props API

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `variant` | `'primary' \| 'secondary' \| 'danger'` | No | `'primary'` | Visual style of the button |
| `size` | `'small' \| 'medium' \| 'large'` | No | `'medium'` | Size of the button |
| `loading` | `boolean` | No | `false` | Shows loading spinner, disables interaction |
| `disabled` | `boolean` | No | `false` | Disables the button |
| `onClick` | `() => void` | No | - | Called when button is clicked |
| `children` | `React.ReactNode` | Yes | - | Button label or content |
| `className` | `string` | No | `''` | Additional CSS classes |
| `aria-label` | `string` | No | - | Accessibility label (required if no text children) |

### Complex Props

**`variant`**: Controls visual appearance
- `primary`: Main call-to-action (blue background)
- `secondary`: Less prominent action (white background, blue border)
- `danger`: Destructive action (red background) - use sparingly

**`loading`**: When `true`:
- Shows spinner icon
- Disables interaction (button not clickable)
- Sets `aria-busy="true"` for screen readers
- **Use case**: After user clicks submit, while waiting for API response
```

**Why this format:**
- ✅ Scannable table for quick reference
- ✅ Type information inline (developers don't need to check code)
- ✅ Required vs optional clearly marked
- ✅ Defaults documented (avoids assumptions)
- ✅ Detailed explanations for complex props

---

### Visual Examples Documentation

**Format**: Code + visual description or screenshot reference

```markdown
## Examples

### Basic Usage

```tsx
import { Button } from '@/components/common/Button';

function App() {
  return (
    <Button onClick={() => alert('Clicked!')}>
      Click Me
    </Button>
  );
}
```

**Renders**: Primary button with blue background, white text "Click Me"

---

### Variants

```tsx
<Button variant="primary">Save</Button>
<Button variant="secondary">Cancel</Button>
<Button variant="danger">Delete</Button>
```

**Renders**: Three buttons side-by-side:
- "Save" (blue background)
- "Cancel" (white background, blue border)
- "Delete" (red background)

---

### Loading State

```tsx
function EnrollForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const handleSubmit = async () => {
    setIsSubmitting(true);
    await enrollUser();
    setIsSubmitting(false);
  };
  
  return (
    <Button loading={isSubmitting} onClick={handleSubmit}>
      Enroll Now
    </Button>
  );
}
```

**Behavior**: 
- Initially: Shows "Enroll Now" text, clickable
- After click: Shows spinner + "Enroll Now" text, not clickable
- After completion: Returns to initial state

---

### Accessibility

```tsx
// ✅ Good: Icon button with aria-label
<Button aria-label="Close modal">
  <CloseIcon />
</Button>

// ❌ Bad: Icon button without aria-label (screen reader can't describe it)
<Button>
  <CloseIcon />
</Button>
```
```

**Why include examples:**
- ✅ Developers can copy-paste working code
- ✅ Visual descriptions clarify expected output
- ✅ Shows common patterns (loading state, accessibility)
- ✅ Documents both correct and incorrect usage

---

### State and Variant Documentation

**Format**: Table or visual matrix

```markdown
## States and Variants

### Visual States

| State | Description | Visual Appearance | Interaction |
|-------|-------------|-------------------|-------------|
| **Default** | Normal resting state | Blue background, white text | Clickable, shows pointer cursor |
| **Hover** | Mouse over button | Darker blue background | Clickable, shows pointer cursor |
| **Active** | Button being pressed | Even darker blue, slight scale down | Momentary state during click |
| **Disabled** | Button cannot be clicked | Gray background, gray text, 50% opacity | Not clickable, shows default cursor |
| **Loading** | Waiting for async operation | Blue background, spinner + text | Not clickable, shows spinner animation |
| **Focus** | Keyboard navigation | Blue background, 2px blue outline | Clickable via Enter/Space keys |

### Variant Styles

| Variant | Background | Text Color | Border | Use Case |
|---------|-----------|------------|--------|----------|
| `primary` | Blue (#007bff) | White | None | Main call-to-action |
| `secondary` | White | Blue (#007bff) | 1px blue | Alternative action |
| `danger` | Red (#dc3545) | White | None | Destructive action (delete, cancel) |

**Design tokens** (if using design system):
- Primary: `var(--color-primary-500)`
- Secondary: `var(--color-neutral-0)` with border `var(--color-primary-500)`
- Danger: `var(--color-danger-500)`
```

---

### Accessibility Documentation

**Format**: ARIA attributes, keyboard support, screen reader behavior

```markdown
## Accessibility

### ARIA Attributes

| Attribute | When Applied | Purpose |
|-----------|--------------|---------|
| `aria-busy="true"` | When `loading={true}` | Announces to screen readers that button is processing |
| `aria-label` | When no text children | Provides accessible name for icon-only buttons |
| `aria-disabled="true"` | When `disabled={true}` | Alternative to `disabled` attribute (semantic) |

### Keyboard Support

| Key | Action |
|-----|--------|
| `Enter` or `Space` | Activates button (calls `onClick`) |
| `Tab` | Moves focus to button |
| `Shift+Tab` | Moves focus away from button |

### Screen Reader Behavior

**Default state**:
```
"Save, button"
```

**Loading state**:
```
"Save, button, busy"
[Spinner announces progress periodically]
```

**Disabled state**:
```
"Save, button, dimmed" (or "unavailable" depending on screen reader)
```

### Accessibility Guidelines

✅ **DO:**
- Always provide `aria-label` for icon-only buttons
- Use semantic `<button>` element (not `<div>` with click handler)
- Ensure 4.5:1 color contrast ratio (WCAG AA)
- Provide loading state feedback for async operations

❌ **DON'T:**
- Use `<div>` or `<span>` as button (breaks keyboard nav)
- Omit `aria-label` on icon-only buttons
- Disable button without explaining why (provide error message)
- Use color alone to convey meaning (add icon or text)

### WCAG Compliance

- ✅ WCAG 2.1 Level AA compliant
- ✅ Keyboard accessible
- ✅ Screen reader compatible
- ✅ Sufficient color contrast
- ✅ Focus indicator visible
```

---

## Enterprise Best Practices for UI Components

### 1. Component Composition Over Configuration

**DO** (Composition):
```tsx
// ✅ Flexible, composable, easy to extend
export function Card({ children, className }: CardProps) {
  return <div className={`card ${className}`}>{children}</div>;
}

export function CardHeader({ children }: CardHeaderProps) {
  return <div className="card-header">{children}</div>;
}

export function CardBody({ children }: CardBodyProps) {
  return <div className="card-body">{children}</div>;
}

// Usage: Developer composes as needed
<Card>
  <CardHeader>
    <h2>Course Title</h2>
  </CardHeader>
  <CardBody>
    <p>Course description...</p>
  </CardBody>
</Card>
```

**DON'T** (Prop explosion):
```tsx
// ❌ Too many props, hard to maintain, inflexible
export function Card({
  title,
  subtitle,
  description,
  image,
  imagePosition,
  actions,
  footer,
  showBorder,
  showShadow,
  headerAlign,
  bodyPadding,
  ...50 more props
}: CardProps) {
  // Complex logic to handle all configurations
}
```

**Document composition pattern**:
```markdown
## Component Composition

This component follows the **Compound Component** pattern. Use sub-components for flexibility:

```tsx
import { Card, CardHeader, CardBody, CardFooter } from '@/components/common/Card';

<Card>
  <CardHeader>Your header content</CardHeader>
  <CardBody>Your body content</CardBody>
  <CardFooter>Your footer content</CardFooter>
</Card>
```

**Benefits**:
- ✅ Flexible composition (use only parts you need)
- ✅ Easy to extend (add new sub-components without breaking changes)
- ✅ Clear visual hierarchy in code
```

---

### 2. Controlled vs Uncontrolled Components

**Controlled** (parent manages state):
```tsx
// ✅ Parent has full control over input value
export function ControlledInput({ value, onChange }: ControlledInputProps) {
  return (
    <input
      type="text"
      value={value}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}

// Usage: Parent manages state
function Form() {
  const [name, setName] = useState('');
  
  return (
    <ControlledInput
      value={name}
      onChange={setName}
    />
  );
}
```

**Uncontrolled** (component manages internal state):
```tsx
// ✅ Component manages its own state, simpler for one-off usage
export function UncontrolledInput({ defaultValue, onSubmit }: UncontrolledInputProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  
  const handleSubmit = () => {
    const value = inputRef.current?.value;
    onSubmit(value);
  };
  
  return (
    <input
      ref={inputRef}
      type="text"
      defaultValue={defaultValue}
    />
  );
}
```

**Hybrid** (supports both patterns):
```tsx
// ✅ Best of both worlds - controlled if value/onChange provided, uncontrolled otherwise
export function Input({
  value,
  defaultValue,
  onChange,
  ...rest
}: InputProps) {
  const [internalValue, setInternalValue] = useState(defaultValue ?? '');
  
  const isControlled = value !== undefined;
  const currentValue = isControlled ? value : internalValue;
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!isControlled) {
      setInternalValue(e.target.value);
    }
    onChange?.(e.target.value);
  };
  
  return (
    <input
      type="text"
      value={currentValue}
      onChange={handleChange}
      {...rest}
    />
  );
}
```

**Document control pattern**:
```markdown
## Component Behavior

### Controlled Mode

Pass both `value` and `onChange` to control the input externally:

```tsx
const [name, setName] = useState('');

<Input
  value={name}
  onChange={setName}
/>
```

### Uncontrolled Mode

Pass only `defaultValue` (or neither) for internal state management:

```tsx
<Input
  defaultValue="John Doe"
  onBlur={(value) => console.log('Final value:', value)}
/>
```

**When to use each**:
- **Controlled**: Form validation, derived state, complex state logic
- **Uncontrolled**: Simple forms, performance-critical scenarios, ref access
```

---

### 3. Props Spreading and Type Safety

**DO** (Typed spreading):
```tsx
// ✅ Extends native HTML attributes, type-safe
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  loading?: boolean;
}

export function Button({ variant, loading, className, ...rest }: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} ${className}`}
      disabled={loading}
      {...rest}  // Spreads all standard HTML button attributes
    />
  );
}

// Usage: All HTML button props work automatically
<Button
  variant="primary"
  onClick={handleClick}
  type="submit"         // Standard HTML attribute
  aria-label="Save"     // Standard ARIA attribute
  data-testid="save"    // Data attribute
/>
```

**DON'T** (Untyped spreading):
```tsx
// ❌ No type safety, any prop accepted
export function Button(props: any) {
  return <button {...props} />;
}
```

**Document extensibility**:
```markdown
## Props API

### Extended HTML Attributes

This component extends `React.ButtonHTMLAttributes<HTMLButtonElement>`, which means **all standard HTML button attributes are supported**:

```tsx
<Button
  variant="primary"      // Custom prop
  onClick={handleClick}  // Standard HTML prop
  type="submit"          // Standard HTML prop
  form="my-form"         // Standard HTML prop
  aria-label="Save"      // Standard ARIA prop
  data-testid="btn"      // Data attribute
  className="my-class"   // Standard className
/>
```

**Common HTML button attributes**:
- `type`: `'button' | 'submit' | 'reset'`
- `disabled`: `boolean`
- `form`: `string` (associates button with form by ID)
- `name`: `string` (for form submission)
- `value`: `string` (for form submission)

See [MDN Button Reference](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/button) for complete list.
```

---

### 4. Performance Optimization

**React.memo for Pure Components**:
```tsx
// ✅ Prevents re-renders when props haven't changed
export const CourseCard = React.memo(function CourseCard({ course }: CourseCardProps) {
  return (
    <Card>
      <h3>{course.title}</h3>
      <p>{course.description}</p>
    </Card>
  );
});

// Custom comparison function for complex props
export const CourseCard = React.memo(
  function CourseCard({ course }: CourseCardProps) {
    // Component implementation
  },
  (prevProps, nextProps) => {
    // Return true if props are equal (don't re-render)
    return prevProps.course.id === nextProps.course.id &&
           prevProps.course.updatedAt === nextProps.course.updatedAt;
  }
);
```

**useCallback for Event Handlers**:
```tsx
// ✅ Memoized callback, prevents child re-renders
export function CourseList({ courses }: CourseListProps) {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  
  // Callback doesn't change between renders (unless courses change)
  const handleCourseClick = useCallback((courseId: string) => {
    setSelectedId(courseId);
  }, []);  // Empty deps - callback never changes
  
  return (
    <div>
      {courses.map(course => (
        <CourseCard
          key={course.id}
          course={course}
          onClick={handleCourseClick}  // Same reference every render
        />
      ))}
    </div>
  );
}
```

**useMemo for Expensive Computations**:
```tsx
// ✅ Memoized computed value
export function CourseStatistics({ enrollments }: CourseStatisticsProps) {
  // Only recompute when enrollments change
  const statistics = useMemo(() => {
    return {
      total: enrollments.length,
      completed: enrollments.filter(e => e.status === 'Completed').length,
      inProgress: enrollments.filter(e => e.status === 'InProgress').length,
      avgCompletionTime: calculateAvgTime(enrollments),
    };
  }, [enrollments]);
  
  return <div>{/* Render statistics */}</div>;
}
```

**Document performance considerations**:
```markdown
## Performance Considerations

### Memoization

This component uses `React.memo` to prevent unnecessary re-renders:

```tsx
export const CourseCard = React.memo(CourseCard);
```

**Re-renders only when**:
- `course.id` changes
- `course.updatedAt` changes

**Does NOT re-render when**:
- Parent component re-renders
- Sibling components update
- Unrelated state changes

### Performance Metrics

**Typical render time**: <5ms (Chrome DevTools Profiler)  
**Re-render frequency**: Low (memoized, pure component)  
**Bundle size**: 2.3 KB (gzipped)

### Optimization Tips

✅ **DO:**
- Pass stable `onClick` handlers (wrap with `useCallback`)
- Use `key` prop in lists (enables React reconciliation)
- Memoize expensive computations with `useMemo`

❌ **DON'T:**
- Pass inline arrow functions as props (creates new function every render)
- Pass new object/array literals as props (creates new reference every render)

```tsx
// ❌ Bad: Creates new function every render
<CourseCard onClick={() => handleClick(course.id)} />

// ✅ Good: Stable reference
const handleClick = useCallback((id) => handleCourseClick(id), []);
<CourseCard onClick={handleClick} />
```
```

---

### 5. Error Boundaries and Error Handling

**Error Boundary Component**:
```tsx
// ✅ Catches errors in child components
export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }
  
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
    // Log to error tracking service (Sentry, LogRocket, etc.)
  }
  
  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }
    
    return this.props.children;
  }
}

// Usage
<ErrorBoundary fallback={<ErrorFallback />}>
  <CourseList />
</ErrorBoundary>
```

**Component-level Error Handling**:
```tsx
// ✅ Graceful error handling with user feedback
export function CourseList() {
  const [error, setError] = useState<Error | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    fetchCourses()
      .then(setCourses)
      .catch(setError)
      .finally(() => setIsLoading(false));
  }, []);
  
  if (error) {
    return (
      <ErrorState
        message="Failed to load courses"
        error={error}
        onRetry={() => window.location.reload()}
      />
    );
  }
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  return <div>{/* Render courses */}</div>;
}
```

**Document error handling**:
```markdown
## Error Handling

### Error Boundary

Wrap this component in an Error Boundary to catch rendering errors:

```tsx
<ErrorBoundary fallback={<ErrorFallback />}>
  <CourseList />
</ErrorBoundary>
```

### Error States

| Error Type | User Experience | Developer Action |
|------------|-----------------|------------------|
| **Network Error** | "Failed to load courses. Try again." with retry button | Logged to console, user can retry |
| **API Error** | "Courses unavailable. Contact support." with support link | Error logged to monitoring service |
| **Render Error** | Error boundary shows fallback UI | Error caught by boundary, reported to Sentry |

### Error Recovery

**Automatic retry**: API calls retry 3 times with exponential backoff  
**Manual retry**: User can click "Try again" button  
**Fallback UI**: Error boundary shows generic error message

### Logging

All errors logged to:
- Browser console (development)
- Application Insights (production)
- Sentry (production - includes user context, stack trace)
```

---

### 6. Testing Patterns

**Unit Tests (Vitest/Jest + React Testing Library)**:
```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders children text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
  
  it('calls onClick when clicked', () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByText('Click me'));
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  it('shows loading spinner when loading', () => {
    render(<Button loading>Submit</Button>);
    
    expect(screen.getByRole('button')).toHaveAttribute('aria-busy', 'true');
    expect(screen.getByText('Submit')).toBeInTheDocument();
  });
  
  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    
    expect(screen.getByRole('button')).toBeDisabled();
  });
});
```

**Document testing guidance**:
```markdown
## Testing

### Unit Tests

Location: `Button.test.tsx`  
Framework: Vitest + React Testing Library  
Coverage: 95%+

### Test Cases

| Scenario | Test | Expected Result |
|----------|------|-----------------|
| **Render** | Renders children | Text content visible |
| **Click** | Click event | `onClick` handler called |
| **Loading** | `loading={true}` | Button disabled, spinner shown, `aria-busy="true"` |
| **Disabled** | `disabled={true}` | Button disabled, not clickable |
| **Variants** | All 3 variants | Correct CSS classes applied |
| **Accessibility** | `aria-label` | Screen reader can identify button |

### Running Tests

```bash
# Run all tests
npm test

# Run Button tests only
npm test Button

# Run with coverage
npm test -- --coverage
```

### Mocking

If component uses external dependencies:

```tsx
// Mock API calls
vi.mock('@/services/api', () => ({
  fetchCourses: vi.fn(() => Promise.resolve(mockCourses))
}));

// Mock child components
vi.mock('@/components/common/Card', () => ({
  Card: ({ children }: any) => <div data-testid="mock-card">{children}</div>
}));
```

### Visual Regression Tests

If using Storybook + Chromatic:
- **Location**: `Button.stories.tsx`
- **Coverage**: All variants, states, sizes
- **CI/CD**: Runs on every PR
```

---

### 7. Accessibility (A11y) Best Practices

**Semantic HTML**:
```tsx
// ✅ Use semantic HTML elements
<button onClick={handleClick}>Click me</button>
<nav><a href="/courses">Courses</a></nav>
<main><article>Content</article></main>
<aside>Sidebar</aside>
<footer>Footer</footer>

// ❌ Don't use div for everything
<div onClick={handleClick}>Click me</div>  // Not keyboard accessible
<div><div>Courses</div></div>               // No semantic meaning
```

**ARIA Attributes**:
```tsx
// ✅ Proper ARIA usage
<button
  aria-label="Close modal"           // Describes button (icon-only)
  aria-pressed={isActive}             // Toggle button state
  aria-expanded={isOpen}              // Disclosure state
  aria-controls="modal-content"       // Related element
>
  <CloseIcon />
</button>

// ❌ Redundant ARIA (button role already implied)
<button role="button" aria-label="A button">Click</button>
```

**Keyboard Navigation**:
```tsx
// ✅ Keyboard accessible modal
export function Modal({ isOpen, onClose, children }: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (isOpen) {
      // Trap focus inside modal
      modalRef.current?.focus();
    }
  }, [isOpen]);
  
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };
  
  if (!isOpen) return null;
  
  return (
    <div
      ref={modalRef}
      role="dialog"
      aria-modal="true"
      tabIndex={-1}
      onKeyDown={handleKeyDown}
    >
      {children}
    </div>
  );
}
```

**Document accessibility**:
```markdown
## Accessibility

### WCAG 2.1 Compliance

- ✅ Level AA compliant
- ✅ Keyboard navigable
- ✅ Screen reader compatible
- ✅ Color contrast ratio: 4.5:1 minimum
- ✅ Focus indicators visible

### Keyboard Support

| Key | Action |
|-----|--------|
| `Tab` | Move focus to button |
| `Shift+Tab` | Move focus to previous element |
| `Enter` or `Space` | Activate button |
| `Escape` | Close (for modals, dropdowns) |

### Screen Reader Testing

**Tested with**:
- NVDA (Windows)
- JAWS (Windows)
- VoiceOver (macOS, iOS)

**Announces as**: "Save, button" (default state)

### Common A11y Mistakes

❌ **DON'T:**
```tsx
// Missing alt text
<img src="course.jpg" />

// Non-semantic clickable div
<div onClick={handleClick}>Click me</div>

// Icon button without label
<button><TrashIcon /></button>

// Form input without label
<input type="text" placeholder="Name" />
```

✅ **DO:**
```tsx
// Descriptive alt text
<img src="course.jpg" alt="Introduction to React course thumbnail" />

// Semantic button
<button onClick={handleClick}>Click me</button>

// Icon button with aria-label
<button aria-label="Delete course"><TrashIcon /></button>

// Form input with label
<label htmlFor="name">Name</label>
<input id="name" type="text" />
```
```

---

## Custom Hooks Documentation

**Custom hooks deserve documentation** when they:
- Manage complex state logic
- Are reused across multiple components
- Have non-obvious behavior
- Accept parameters or return complex values

**Hook documentation structure**:

```markdown
# Hook: useAuth

**File**: `src/hooks/useAuth.ts`  
**Type**: State management hook  
**Dependencies**: React Context, Local Storage

---

## Purpose

Provides authentication state and actions to components. Manages user session, token storage, and login/logout operations.

## Usage

```tsx
import { useAuth } from '@/hooks/useAuth';

function MyComponent() {
  const { user, isAuthenticated, login, logout } = useAuth();
  
  if (!isAuthenticated) {
    return <LoginForm onLogin={login} />;
  }
  
  return <div>Welcome, {user.name}!</div>;
}
```

## API

### Return Value

| Property | Type | Description |
|----------|------|-------------|
| `user` | `User \| null` | Current authenticated user, or `null` if not logged in |
| `isAuthenticated` | `boolean` | `true` if user is logged in |
| `isLoading` | `boolean` | `true` while checking authentication status |
| `login` | `(credentials) => Promise<void>` | Authenticate user with credentials |
| `logout` | `() => void` | Clear session and log out user |
| `refreshToken` | `() => Promise<void>` | Refresh authentication token |

### Error Handling

Throws `AuthenticationError` if:
- Invalid credentials provided
- Token expired and refresh failed
- Network error during authentication

## Implementation Details

- **Token storage**: Local storage (key: `auth_token`)
- **Token refresh**: Automatic refresh 5 minutes before expiration
- **Logout behavior**: Clears local storage, redirects to `/login`
- **Context provider**: Must wrap app with `<AuthProvider>`

## Example: Protected Route

```tsx
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) return <LoadingSpinner />;
  if (!isAuthenticated) return <Navigate to="/login" />;
  
  return <>{children}</>;
}
```
```

---

## Cross-Repository Integration

### Linking to Backend API Documentation

**When component calls backend APIs:**

```markdown
## Data Fetching

This component fetches data from the backend API:

### API Endpoints Used

| Endpoint | Method | Purpose | Documentation |
|----------|--------|---------|---------------|
| `/api/courses` | GET | Fetch course list | [API Docs](../../api-repo/docs/endpoints/courses.md) |
| `/api/enrollments` | POST | Create enrollment | [API Docs](../../api-repo/docs/endpoints/enrollments.md) |

### Service Layer

API calls handled by `courseService.ts`:
- See [courseService documentation](../services/courseService_doc.md)

### Data Models

| Model | Source | Documentation |
|-------|--------|---------------|
| `Course` | Backend API | [Course entity](../../api-repo/docs/models/Course.md) |
| `Enrollment` | Backend API | [Enrollment entity](../../api-repo/docs/models/Enrollment.md) |
```

### Linking to Design System

**When component uses design tokens:**

```markdown
## Styling and Theming

### Design System

This component follows the [Company Design System v2.0](https://design-system.company.com).

### Design Tokens

| Token | CSS Variable | Value | Usage |
|-------|-------------|-------|-------|
| Primary color | `--color-primary-500` | `#007bff` | Button background |
| Text color | `--color-neutral-900` | `#1a1a1a` | Button text |
| Border radius | `--radius-md` | `4px` | Button corners |
| Spacing | `--space-3` | `12px` | Button padding |

### Figma

Design spec: [Button Component](https://figma.com/file/ABC123/Button)
```

---

## Common Anti-Patterns to Avoid

### ❌ Don't: Prop Drilling

**Bad** (passing props through many levels):
```tsx
// ❌ Deep prop drilling - hard to maintain
function App() {
  const [user, setUser] = useState<User>();
  return <Dashboard user={user} />;
}

function Dashboard({ user }: { user: User }) {
  return <Sidebar user={user} />;
}

function Sidebar({ user }: { user: User }) {
  return <UserMenu user={user} />;
}

function UserMenu({ user }: { user: User }) {
  return <div>{user.name}</div>;
}
```

**Good** (use Context or state management):
```tsx
// ✅ Context API - clean component tree
const UserContext = createContext<User | null>(null);

function App() {
  const [user, setUser] = useState<User>();
  return (
    <UserContext.Provider value={user}>
      <Dashboard />
    </UserContext.Provider>
  );
}

function UserMenu() {
  const user = useContext(UserContext);
  return <div>{user?.name}</div>;
}
```

---

### ❌ Don't: Massive Components

**Bad** (1000+ line component):
```tsx
// ❌ God component - does everything
function Dashboard() {
  // 50 lines of state
  // 200 lines of data fetching logic
  // 300 lines of event handlers
  // 500 lines of JSX
  return (
    <div>
      {/* Hundreds of lines of JSX */}
    </div>
  );
}
```

**Good** (split into smaller components):
```tsx
// ✅ Small, focused components
function Dashboard() {
  return (
    <div>
      <DashboardHeader />
      <DashboardStats />
      <DashboardCharts />
      <DashboardActivity />
    </div>
  );
}

// Each sub-component is 50-200 lines, focused, testable
```

---

### ❌ Don't: Missing Key Prop in Lists

**Bad** (no key or index as key):
```tsx
// ❌ No key - React can't optimize re-renders
<ul>
  {courses.map(course => (
    <li>{course.title}</li>
  ))}
</ul>

// ❌ Index as key - breaks when list reorders
<ul>
  {courses.map((course, index) => (
    <li key={index}>{course.title}</li>
  ))}
</ul>
```

**Good** (stable, unique key):
```tsx
// ✅ Unique, stable ID as key
<ul>
  {courses.map(course => (
    <li key={course.id}>{course.title}</li>
  ))}
</ul>
```

---

### ❌ Don't: Direct DOM Manipulation

**Bad** (bypassing React):
```tsx
// ❌ Direct DOM manipulation - breaks React's reconciliation
function Component() {
  useEffect(() => {
    document.getElementById('my-element').innerHTML = '<div>Content</div>';
  }, []);
  
  return <div id="my-element"></div>;
}
```

**Good** (let React manage DOM):
```tsx
// ✅ Use React state and JSX
function Component() {
  const [content, setContent] = useState('<div>Content</div>');
  
  return <div dangerouslySetInnerHTML={{ __html: content }} />;
  // Or better: parse and render as React components
}
```

---

### ❌ Don't: Inline Styles Everywhere

**Bad** (inline styles, no reusability):
```tsx
// ❌ Inline styles - no reusability, specificity issues
<button style={{
  backgroundColor: '#007bff',
  color: 'white',
  padding: '12px 24px',
  borderRadius: '4px',
  border: 'none'
}}>
  Click me
</button>
```

**Good** (CSS modules or styled-components):
```tsx
// ✅ CSS modules - reusable, maintainable
import styles from './Button.module.css';

<button className={styles.primary}>
  Click me
</button>

// Button.module.css
.primary {
  background-color: var(--color-primary);
  color: white;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  border: none;
}
```

---

## Quick Reference

### Creating Component Documentation

**Steps:**
1. Copy `ui_component_template.md` to `docs/components/[ComponentName]_doc.md`
2. Use Copilot to generate baseline (5-10 minutes)
3. Enhance with visual examples, accessibility notes (10-15 minutes)
4. Add optional sections as needed
5. Create PR with feature tag

**Time**: ~20 minutes for baseline documentation

---

### Reviewing Component Documentation PRs

**Checklist:**
- [ ] Purpose and usage clear?
- [ ] All props documented with types?
- [ ] At least 1 visual example included?
- [ ] Accessibility considerations documented?
- [ ] States/variants documented (if applicable)?
- [ ] Follows AKR_CHARTER_UI.md conventions?

---

## Questions & Support

**Questions about UI conventions?**
- Reference this charter (AKR_CHARTER_UI.md)
- Check universal charter (AKR_CHARTER.md)
- Check Design System documentation (if exists)
- Ask UI/UX team or Tech Lead

**Proposing changes to UI conventions?**
- Open PR with rationale
- Tag UI team for review
- Expect cross-team discussion

**Need help documenting complex component?**
- Check templates for structure
- Ask team for examples
- Use Copilot to generate first draft
- Focus on user experience, not implementation details

---

**Remember**: Document to help developers USE the component, not just understand the code. The best component documentation shows examples and explains behavior, not just lists props.

---

**AKR Charter: UI Component - End of Document**
