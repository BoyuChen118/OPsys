#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdbool.h>

extern int next_thread_id;
extern int max_squares;
extern char ***dead_end_boards; /* do NOT free this memory in hw3.c */
int boardRows, boardCols = 0;
int deadEndThreshold;
int deadEndIndex = 0;
pthread_t originThread;
int solutions = 0;
int deadEndStorageLength = 4;
pthread_mutex_t lock;
/*
NOTE: check moves counter clockwise
*/

typedef struct
{
    //Or whatever information that you need
    int **board;
    int currentRow;
    int currentCol;
    int id;
    int current_squares;
} arguments;

typedef struct
{
    int id;
    int squares_covered;
} retarguments;

void printBoard(int **board)
{ // for debugging
    printf("\n");
    for (int i = 0; i <= boardRows; i++)
    {
        for (int j = 0; j <= boardCols; j++)
        {
            printf("%d", board[i][j]);
        }
        printf("\n");
    }
}
void makeNextMove(int *r, int *c, int movenum, int *current_squares, int **board)
{
    switch (movenum)
    {
    case 0:
        *r += 1;
        *c += 2;
        break;
    case 1:
        *r -= 1;
        *c += 2;
        break;
    case 2:
        *r -= 2;
        *c += 1;
        break;
    case 3:
        *r -= 2;
        *c -= 1;
        break;
    case 4:
        *r -= 1;
        *c -= 2;
        break;
    case 5:
        *r += 1;
        *c -= 2;
        break;
    case 6:
        *r += 2;
        *c -= 1;
        break;

    default:
        *r += 2;
        *c += 1;
        break;
    }
    if (*r > boardRows || *c > boardCols)
    {
        fprintf(stderr, "Out of bound, r is %d, c is %d\n", *r, *c);
        return;
    }
    board[(int)*r][(int)*c] = *current_squares;
    (*current_squares) += 1;
}
int determineNextMove(int **board, int row, int col, int *moveCounter, int *lastMove)
{ // determine the next available move (in number)
    int counter = 0;
    int nextMove = -1;
    if (row + 1 <= boardRows && col + 2 <= boardCols && board[row + 1][col + 2] == -1)
    { // row+1, col+2,  movenum: 0
        counter++;
        if (*lastMove <= -1 && nextMove == -1)
        {
            nextMove = 0;
        }
    }

    if (row - 1 >= 0 && col + 2 <= boardCols && board[row - 1][col + 2] == -1)
    { // row-1, col+2, movenum:1
        counter++;
        if (*lastMove <= 0 && nextMove == -1)
        {
            nextMove = 1;
        }
    }

    if (row - 2 >= 0 && col + 1 <= boardCols && board[row - 2][col + 1] == -1)
    { // row-2, col+1, movenum:2
        counter++;
        if (*lastMove <= 1 && nextMove == -1)
        {
            nextMove = 2;
        }
    }

    if (row - 2 >= 0 && col - 1 >= 0 && board[row - 2][col - 1] == -1)
    { // row-2, col-1, movenum:3
        counter++;
        if (*lastMove <= 2 && nextMove == -1)
        {
            nextMove = 3;
        }
    }

    if (row - 1 >= 0 && col - 2 >= 0 && board[row - 1][col - 2] == -1)
    { // row-1, col-2, movenum:4
        counter++;
        if (*lastMove <= 3 && nextMove == -1)
        {
            nextMove = 4;
        }
    }

    if (row + 1 <= boardRows && col - 2 >= 0 && board[row + 1][col - 2] == -1)
    { // row+1, col-2, movenum:5
        counter++;
        if (*lastMove <= 4 && nextMove == -1)
        {
            nextMove = 5;
        }
    }

    if (row + 2 <= boardRows && col - 1 >= 0 && board[row + 2][col - 1] == -1)
    { // row+2, col-1, movenum:6
        counter++;
        if (*lastMove <= 5 && nextMove == -1)
        {
            nextMove = 6;
        }
    }
    if (row + 2 <= boardRows && col + 1 <= boardCols && board[row + 2][col + 1] == -1)
    { // row+2, col+1, movenum:7
        counter++;
        if (*lastMove <= 6 && nextMove == -1)
        {
            nextMove = 7;
        }
    }

    *moveCounter = counter;
    *lastMove = nextMove;
    return nextMove;
}

void *findNextMove(void *ar)
{ // find the nextpossible move based on parameters passed in
    arguments *a = ar;
    int **board = a->board;
    int currentRow = a->currentRow;
    int currentCol = a->currentCol;
    int thread_id = a->id;
    int current_squares = a->current_squares;
    int largestChild = 0;
    int moveCounter = 0; // keeps track of how many moves are available given the current board state and position
    int lastMove = -1;
    retarguments *ret = malloc(sizeof *ret);
    char *display = malloc(10 * sizeof(char));
    if (pthread_self() != originThread)
    {
        sprintf(display, "%s %d:", "THREAD", thread_id);
    }
    else
    {
        sprintf(display, "%s:", "MAIN");
    }

    int next = determineNextMove(board, currentRow, currentCol, &moveCounter, &lastMove);

    if (moveCounter == 0)
    { // deal with dead end board

        // free(args);

        if (current_squares < deadEndThreshold)
        { // free the board if covered squares is lower than threshold
            printf("%s Dead end at move #%d\n", display, current_squares);
            for (int i = 0; i <= boardRows; i++)
            {
                free(board[i]);
            }
            free(board);
        }
        else if (current_squares == (boardRows + 1) * (boardCols + 1))
        { // solution is found
            printf("%s Sonny found a full knight's tour!\n", display);
            solutions++;
        }
        else
        { // update dead end boards with new dead end boardf
            printf("%s Dead end at move #%d\n", display, current_squares);
            pthread_mutex_lock(&lock);
            if(deadEndIndex >= deadEndStorageLength){ // allocate space for dead end storage if there isn't enough space
                dead_end_boards = realloc(dead_end_boards, (deadEndStorageLength + 1) * sizeof(char **));
                deadEndStorageLength++;
            }

            dead_end_boards[deadEndIndex] = calloc(boardRows + 1, sizeof(char *));
            for (int i = 0; i <= boardRows; i++)
            {
                dead_end_boards[deadEndIndex][i] = calloc(boardCols + 1, sizeof(char));
                for (int j = 0; j <= boardCols; j++)
                {
                    if (board[i][j] != -1)
                        dead_end_boards[deadEndIndex][i][j] = 'S';
                    else
                        dead_end_boards[deadEndIndex][i][j] = '.';
                }
            }
            deadEndIndex++;
            pthread_mutex_unlock(&lock);
        }
        ret->squares_covered = current_squares;
        ret->id = thread_id;
        if (pthread_self() == originThread)
        {
            return ret;
        }
        pthread_exit(ret);
        // exit the function & report back to its parent thread the squares it covered
    }
    else if (moveCounter < 0)
    {
        fprintf(stderr, "Something wrong with movecounter.");
    }
    else if (moveCounter == 1)
    { // don't create new thread continue on this thread til find multiple available moves
        makeNextMove(&currentRow, &currentCol, next, &current_squares, board);
        arguments *newArgs = malloc(sizeof *newArgs);
        newArgs->board = board;
        newArgs->currentRow = currentRow;
        newArgs->currentCol = currentCol;
        newArgs->current_squares = current_squares;
        newArgs->id = thread_id;
        //printf("(%d,%d), last move is %d, thread is %d\n", currentRow, currentCol, next,thread_id);
        findNextMove(newArgs);
    }
    else
    { // create new threads
        pthread_t tids[8];

        printf("%s %d possible moves after move #%d; creating %d child threads...\n", display, moveCounter, current_squares, moveCounter);
        for (int i = 0; i < 8; i++)
        {
            tids[i] = -1;
        }
        int tidCounter = 0;
        int n = next;
        while (n != -1)
        {
            int error;
            // makeNextMove(&currentRow, &currentCol, n, &current_squares, board);
            int **duplicateboard = calloc(boardRows + 1, sizeof(int *));
            for (int i = 0; i <= boardRows; i++)
            {
                duplicateboard[i] = calloc(boardCols + 1, sizeof(int));
                for (int j = 0; j <= boardCols; j++)
                {
                    duplicateboard[i][j] = board[i][j];
                }
            }
            arguments *args = malloc(sizeof *args);
            args->board = duplicateboard;
            args->currentCol = currentCol;
            args->currentRow = currentRow;
            args->id = next_thread_id;
            args->current_squares = current_squares;
            makeNextMove(&args->currentRow, &args->currentCol, n, &args->current_squares, args->board);
            error = pthread_create(&(tids[tidCounter]),
                                   NULL,
                                   &findNextMove, args);
            //printf("Thread %d is created!!!!!!!!!!!!\n", args->id);
            next_thread_id++;
#ifdef NO_PARALLEL
            retarguments *retFromChild;
            error = pthread_join(tids[tidCounter], (void **)&retFromChild);
            printf("%s Thread %d joined (returned %d)\n", display, retFromChild->id, retFromChild->squares_covered);
            int potentialHigh = retFromChild->squares_covered;
            if (error != 0)
            {
                fprintf(stderr, "error detected, error num: %d\n", error);
            }
            if (potentialHigh > max_squares)
            {
                max_squares = potentialHigh;
            }
            if (potentialHigh > largestChild)
            {

                largestChild = potentialHigh;
                //printf("set largest child to %d in thread %d",largestChild,thread_id);
            }
#endif
            if (error != 0)
            {
                fprintf(stderr, "ERROR: Thread can't be created");
            }
            n = determineNextMove(board, currentRow, currentCol, &moveCounter, &lastMove);
            tidCounter++;
        }
#ifndef NO_PARALLEL
        for (int i = 0; i < tidCounter; i++)
        {

            if (tids[i] != -1)
            {
                retarguments *retFromChild;
                int error;
                error = pthread_join(tids[i], (void **)&retFromChild);
                printf("%s Thread %d joined (returned %d)\n", display, retFromChild->id, retFromChild->squares_covered);
                int potentialHigh = retFromChild->squares_covered;
                if (error != 0)
                {
                    fprintf(stderr, "error detected, error num: %d\n", error);
                }
                if (potentialHigh > max_squares)
                {
                    max_squares = potentialHigh;
                }
                if (potentialHigh > largestChild)
                {
                    largestChild = potentialHigh;
                }
            }
            else
            {
                printf("not valid thread: %ld\n", tids[i]);
            }
        }
#endif
    }
    ret->id = thread_id;
    // printf("thread %d will return with %d covered\n",thread_id, largestChild);
    ret->squares_covered = largestChild;
    free(display);
    if (pthread_self() != originThread)
        pthread_exit(ret);
    else
        return ret;
}
int simulate(int argc, char *argv[])
{
    if (argc != 6)
    {
        fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: a.out <m> <n> <r> <c> <x>");
        return EXIT_FAILURE;
    }
    setvbuf(stdout, NULL, _IONBF, 0);
    int rows = atoi(argv[1]);
    int cols = atoi(argv[2]);
    boardRows = rows - 1;
    boardCols = cols - 1;
    int startingRow = atoi(argv[3]);
    int startingCol = atoi(argv[4]);
    deadEndThreshold = atoi(argv[5]); // only store dead end boards with at least this threshold squares covered
    if (rows < 2 || cols < 2 || startingRow >= rows || startingCol >= cols || startingRow < 0 || startingCol < 0 || deadEndThreshold > rows * cols)
    {
        fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: a.out <m> <n> <r> <c> <x>");
        return EXIT_FAILURE;
    }

    printf("MAIN: Solving Sonny's knight's tour problem for a %dx%d board\n", rows, cols);
    printf("MAIN: Sonny starts at row %d and column %d (move #1)\n", startingRow, startingCol);
    int **board = calloc(rows, sizeof(int *));
    for (int i = 0; i < rows; i++)
    {
        board[i] = calloc(cols, sizeof(int));
        for (int j = 0; j < cols; j++)
        {
            board[i][j] = -1; // initialize every square to -1
        }
    }

    board[startingRow][startingCol] = 0; // set initial position to 0

    arguments *a = malloc(sizeof *a);
    a->board = board;
    a->currentRow = startingRow;
    a->currentCol = startingCol;
    a->id = next_thread_id;
    a->current_squares = 1;
    originThread = pthread_self();
    retarguments *retarg = findNextMove(a);
    if (retarg->squares_covered > max_squares)
    {
        max_squares = retarg->squares_covered;
    }
    if (solutions)
        printf("MAIN: All threads joined; found %d possible ways to achieve a full knight's tour\n", solutions);
    else if (max_squares == 1)
        printf("MAIN: All threads joined; best solution(s) visited %d square out of %d\n", max_squares, (boardRows + 1) * (boardCols + 1));
    else
        printf("MAIN: All threads joined; best solution(s) visited %d squares out of %d\n", max_squares, (boardRows + 1) * (boardCols + 1));

    //print deadEnd boards

    if (deadEndThreshold == 1 && !solutions)
        printf("MAIN: Dead end board%s covering at least %d square:\n", deadEndIndex != 1 ? "s" : "", deadEndThreshold);
    else if (deadEndThreshold != 1 && !solutions)
        printf("MAIN: Dead end board%s covering at least %d squares:\n", deadEndIndex != 1 ? "s" : "", deadEndThreshold);
    if (!solutions)
    {
        for (int i = 0; i < deadEndIndex; i++)
        {
            for (int r = 0; r <= boardRows; r++)
            {
                if (r == 0)
                    printf("MAIN: >>");
                else
                    printf("MAIN:   ");
                for (int c = 0; c <= boardCols; c++)
                {
                    printf("%c", dead_end_boards[i][r][c]);
                }
                if (r == boardRows)
                    printf("<<");
                printf("\n");
            }
        }
    }

    return EXIT_SUCCESS;
}